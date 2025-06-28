import time
import logging
from playwright.sync_api import sync_playwright
from flask import Flask
import os
import schedule
import requests

# ==================== CONFIG ====================
BOT_TOKEN = "7368887153:AAHs8C2IVjTi7RSAqlorG86x3TMkDm8TdMM"  # Your Telegram bot token
CHAT_ID = "1774833565"                         # Your Telegram chat ID
URL_TO_MONITOR = "https://www.lenovo.com/in/outletin/en/laptops/"
CHECK_INTERVAL = 60  # Check every 60 seconds

# ==================== LOGGING ====================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# ==================== FLASK APP ====================
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Lenovo Bot is alive and watching laptop listings."

# ==================== TELEGRAM UTILITY ====================
def send_message(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": msg}
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code != 200:
            logging.warning(f"Telegram send failed: {response.text}")
        else:
            logging.info(f"Telegram message sent: {msg}")
    except Exception as e:
        logging.error(f"Error sending Telegram message: {e}")

# ==================== MONITOR FUNCTION ====================
def check_lenovo():
    old_titles = set()
    max_retries = 3
    retry_delay = 5

    def fetch_page():
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            page.goto(URL_TO_MONITOR, wait_until="networkidle")
            page.wait_for_selector("div.product-tile", state="visible", timeout=10000)
            
            logging.info(f"Page title: {page.title()}")
            content = page.content()[:500]
            logging.info(f"Page content snippet: {content}")
            
            divs = page.query_selector_all("div")
            div_classes = [div.get_attribute("class") for div in divs if div.get_attribute("class")]
            logging.info(f"Found div classes: {div_classes}")

            selectors = [
                "div.product-info__title",
                "h3.product-info__title",
                "div.product-tile__title",
                "div[data-testid='product-title']"
            ]
            titles = []
            for selector in selectors:
                title_elements = page.query_selector_all(selector)
                if title_elements:
                    titles = [el.text_content().strip() for el in title_elements if el.text_content().strip()]
                    logging.info(f"Matched selector '{selector}' with titles: {titles}")
                    break
            
            if not titles:
                logging.warning("No titles found with any selector. Page structure may have changed.")
                titles = []
            browser.close()
            return titles

    while True:
        for attempt in range(max_retries):
            try:
                new_titles = fetch_page()
                if not new_titles:
                    raise ValueError("No titles found, page might have changed.")

                added = [title for title in new_titles if title not in old_titles]
                removed = [title for title in old_titles if title not in new_titles]

                if added:
                    send_message(f"🆕 New Laptops: {', '.join(added)}")
                if removed:
                    send_message(f"❌ Removed Laptops: {', '.join(removed)}")

                old_titles = set(new_titles)
                break

            except Exception as e:
                logging.error(f"Scraping error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    send_message(f"⚠️ Scraping failed after {max_retries} attempts: {e}")

        time.sleep(CHECK_INTERVAL)

# ==================== SCHEDULE MONITORING ====================
def start_monitoring():
    schedule.every(CHECK_INTERVAL).seconds.do(check_lenovo)
    send_message("✅ Lenovo Bot is now live and monitoring every 60 seconds.")
    logging.info("Monitoring thread started")
    while True:
        schedule.run_pending()
        time.sleep(1)

# ==================== RUN FLASK APP ====================
if __name__ == "__main__":
    import threading
    threading.Thread(target=start_monitoring, daemon=True).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

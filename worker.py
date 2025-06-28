import time
import logging
import os
import requests
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# ==================== CONFIG ====================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "7368887153:AAHs8C2IVjTi7RSAqlorG86x3TMkDm8TdMM")
CHAT_ID = os.environ.get("CHAT_ID", "1774833565")
URL_TO_MONITOR = "https://www.lenovo.com/in/outletin/en/laptops/"
CHECK_INTERVAL = int(os.environ.get("CHECK_INTERVAL", 60))  # In seconds

# ==================== LOGGING ====================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# ==================== TELEGRAM UTILITY ====================
def send_message(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": msg[:4096]}  # Limit to 4096 chars
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code != 200:
            logging.warning(f"Telegram send failed: {response.text}")
        else:
            logging.info(f"Telegram message sent: {msg[:50]}...")
    except Exception as e:
        logging.error(f"Error sending Telegram message: {e}")

# ==================== MONITOR FUNCTION ====================
def check_lenovo():
    old_titles = set()
    max_retries = 3
    retry_delay = 5

    def fetch_page():
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
                page.goto(URL_TO_MONITOR, wait_until="networkidle")
                page.wait_for_selector("div.product-tile", state="visible", timeout=10000)
                
                logging.info(f"Page title: {page.title()}")
                content = page.content()[:1000]  # Log first 1000 chars for debugging
                logging.info(f"Page content snippet: {content}")
                
                divs = page.query_selector_all("div")
                div_classes = [div.get_attribute("class") for div in divs if div.get_attribute("class")]
                logging.info(f"Found div classes: {div_classes[:50]}")  # Limit to 50 for readability

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
                        logging.info(f"Matched selector '{selector}' with titles: {titles[:5]}...")  # Limit to 5
                        break
                
                if not titles:
                    logging.warning("No titles found with any selector. Page structure may have changed.")
                    logging.info(f"Full content snippet for debug: {page.content()[:2000]}")
                browser.close()
                return titles
        except PlaywrightTimeoutError as e:
            logging.error(f"Playwright timeout: {e}")
            return []
        except Exception as e:
            logging.error(f"Scraping error: {e}")
            return []

    while True:
        for attempt in range(max_retries):
            new_titles = fetch_page()
            if new_titles:
                added = [title for title in new_titles if title not in old_titles]
                removed = [title for title in old_titles if title not in new_titles]

                if added:
                    send_message(f"🆕 New Laptops: {', '.join(added)}")
                if removed:
                    send_message(f"❌ Removed Laptops: {', '.join(removed)}")

                old_titles = set(new_titles)
                break
            elif attempt == max_retries - 1:
                send_message(f"⚠️ Scraping failed after {max_retries} attempts")

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    send_message("✅ Lenovo Worker Bot is now live and monitoring every 60 seconds.")
    logging.info("Monitoring started")
    check_lenovo()

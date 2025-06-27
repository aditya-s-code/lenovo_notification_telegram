import time
import requests
from bs4 import BeautifulSoup
from flask import Flask
import threading
import os
import logging

# ==================== CONFIG ====================

BOT_TOKEN = "7368887153:AAHs8C2IVjTi7RSAqlorG86x3TMkDm8TdMM"
CHAT_ID = "7368887153"
URL_TO_MONITOR = "https://www.lenovo.com/in/outletin/en/laptops/"
CHECK_INTERVAL = 60  # in seconds

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
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            logging.warning(f"Telegram send failed: {response.text}")
        else:
            logging.info(f"Telegram message sent: {msg}")
    except Exception as e:
        logging.error(f"Error sending Telegram message: {e}")

# ==================== MONITOR FUNCTION ====================

def check_lenovo():
    old_titles = []

    # ✅ One-time startup message
    send_message("✅ Lenovo Bot is now live and monitoring every 60 seconds.")

    while True:
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            html = requests.get(URL_TO_MONITOR, headers=headers, timeout=10).text
            soup = BeautifulSoup(html, "html.parser")
            products = soup.select("div.product-info__title")

            new_titles = [p.text.strip() for p in products]
            added = [title for title in new_titles if title not in old_titles]
            removed = [title for title in old_titles if title not in new_titles]

            for title in added:
                send_message(f"🆕 New Laptop: {title}")

            for title in removed:
                send_message(f"❌ Removed: {title}")

            old_titles = new_titles

        except Exception as e:
            logging.error(f"Scraping error: {e}")
            send_message(f"⚠️ Scraping error: {e}")

        time.sleep(CHECK_INTERVAL)

# ==================== START BACKGROUND MONITORING ====================

threading.Thread(target=check_lenovo, daemon=True).start()

# ==================== RUN FLASK APP (RENDER DEPLOY) ====================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

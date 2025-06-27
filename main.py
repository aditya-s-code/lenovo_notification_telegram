import time
import requests
from bs4 import BeautifulSoup
from flask import Flask
import threading
import os  # ✅ Required to read dynamic PORT on Render

# ✅ Telegram bot details
BOT_TOKEN = "7368887153:AAHs8C2IVjTi7RSAqlorG86x3TMkDm8TdMM"
CHAT_ID = "7368887153"  # Only your numeric user ID

# ✅ Flask app to keep bot alive on Render
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Lenovo Bot is alive!"

# ✅ Function to send Telegram messages
def send_message(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": msg
    }
    requests.post(url, data=payload)

# ✅ Function to check Lenovo laptops
def check_lenovo():
    old_titles = []

    # ✅ One-time test message to confirm bot started
    send_message("✅ Test: Lenovo Bot is running and will notify you every 60 seconds if laptops are added or removed.")

    while True:
        try:
            url = "https://www.lenovo.com/in/outletin/en/laptops/"
            headers = {"User-Agent": "Mozilla/5.0"}
            html = requests.get(url, headers=headers).text
            soup = BeautifulSoup(html, "html.parser")
            products = soup.select("div.product-info__title")
            new_titles = [p.text.strip() for p in products]

            # ✅ Detect laptops added
            added = [title for title in new_titles if title not in old_titles]
            for title in added:
                send_message(f"🆕 Laptop added: {title}")

            # ✅ Detect laptops removed
            removed = [title for title in old_titles if title not in new_titles]
            for title in removed:
                send_message(f"❌ Laptop removed: {title}")

            # ✅ Update old list
            old_titles = new_titles

        except Exception as e:
            send_message(f"⚠️ Error: {str(e)}")

        time.sleep(60)  # ✅ Check every 60 seconds

# ✅ Start monitoring in background thread
threading.Thread(target=check_lenovo).start()

# ✅ Render requires dynamic port
port = int(os.environ.get("PORT", 8080))
app.run(host="0.0.0.0", port=port)

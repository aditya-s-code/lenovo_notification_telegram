import time
import requests
from bs4 import BeautifulSoup
from flask import Flask
import threading
import os

# ✅ Your actual Telegram Bot Token
BOT_TOKEN = "7368887153:AAHs8C2IVjTi7RSAqlorG86x3TMkDm8TdMM"

# ✅ Your actual Telegram Chat ID (use numeric ID, not the token again)
CHAT_ID = "7368887153"  # ✅ This should just be your user/chat ID, not the token

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def check_lenovo():
    old_titles = []
    while True:
        try:
            url = "https://www.lenovo.com/in/outletin/en/laptops/"
            headers = {"User-Agent": "Mozilla/5.0"}
            html = requests.get(url, headers=headers).text
            soup = BeautifulSoup(html, "html.parser")
            products = soup.select("div.product-info__title")

            new_titles = [p.text.strip() for p in products]

            for title in new_titles:
                if title not in old_titles:
                    send_message(f"🆕 New Lenovo laptop: {title}")
            old_titles = new_titles

        except Exception as e:
            send_message(f"⚠️ Error: {str(e)}")

        time.sleep(900)  # 15 minutes

def send_message(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg}
    try:
        requests.post(url, data=payload)
    except:
        pass

# Run the checker in the background
threading.Thread(target=check_lenovo, daemon=True).start()

# Use dynamic port for Render
port = int(os.environ.get("PORT", 8080))
app.run(host="0.0.0.0", port=port)

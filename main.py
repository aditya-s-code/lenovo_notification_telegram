import time
import requests
from bs4 import BeautifulSoup
from flask import Flask
import threading

# ✅ Your correct Telegram bot token and chat ID
BOT_TOKEN = "7368887153:AAHs8C2IVjTi7RSAqlorG86x3TMkDm8TdMM"
CHAT_ID = "1774833565"

# ✅ Create Flask app to keep Render happy
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot is alive!"

# ✅ This checks Lenovo's Outlet every 15 minutes
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

# ✅ This sends Telegram messages
def send_message(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg}
    requests.post(url, data=payload)

# ✅ Run both Flask and the bot
send_message("✅ Test: Lenovo Bot is working!")

threading.Thread(target=check_lenovo).start()
app.run(host="0.0.0.0", port=8080)

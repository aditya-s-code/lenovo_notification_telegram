import logging
import os
from flask import Flask

# ==================== CONFIG ====================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# ==================== FLASK APP ====================
app = Flask(__name__)

@app.route('/')
def home():
    logging.info("Home page accessed")
    return "🤖 Lenovo Bot is alive and watching laptop listings."

@app.route('/health')
def health():
    logging.info("Health check passed")
    return {"status": "healthy"}, 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

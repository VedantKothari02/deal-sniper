import logging
import requests
import html
from config import BOT_TOKEN, ALERT_CHAT_ID, DRY_RUN

logger = logging.getLogger(__name__)

def send_alert(product_data: dict, score: int):
    """
    Formats the deal and sends an alert to Telegram, or logs to console if DRY_RUN = True.
    """
    name = product_data.get('product_name', 'Unknown')
    # Escape HTML characters so Telegram parsing doesn't break
    name = html.escape(name)

    price = product_data.get('price', 0)
    mrp = product_data.get('mrp', 0)
    discount = product_data.get('discount', 0)
    url = product_data.get('url', '')

    # Recalculate discount based on final price and mrp if missing
    if discount == 0 and mrp > 0:
        discount = round(((mrp - price) / mrp) * 100, 2)

    message = (
        f"⚡ Deal Detected\n\n"
        f"Product: {name}\n"
        f"Price: ₹{price}\n"
        f"MRP: ₹{mrp}\n"
        f"Discount: {discount}%\n\n"
        f"Link: {url}"
    )

    if DRY_RUN:
        print("\n--- [DRY RUN] Deal Detected ---")
        print(message)
        print("-------------------------------\n")
        logger.info(f"[DRY RUN] Alert skipped for {name} ({url})")
        return

    if not BOT_TOKEN or not ALERT_CHAT_ID:
        logger.error("BOT_TOKEN or ALERT_CHAT_ID is missing. Cannot send Telegram alert.")
        return

    telegram_api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": ALERT_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(telegram_api_url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info(f"Telegram alert sent for: {name}")
    except Exception as e:
        logger.error(f"Failed to send Telegram alert: {e}")

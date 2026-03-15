import sqlite3
import time
import logging
import os

logger = logging.getLogger(__name__)

DB_PATH = "storage/deals.db"

def init_db():
    """Initializes the SQLite database and creates the required tables."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Alerts table (tracks last alert time for duplicate prevention)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            product_id TEXT,
            site TEXT,
            price REAL,
            timestamp INTEGER,
            last_alert_time INTEGER,
            PRIMARY KEY (product_id, site)
        )
    ''')

    # Price history table (tracks every price seen for a product)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT,
            site TEXT,
            price REAL,
            timestamp INTEGER
        )
    ''')

    conn.commit()
    conn.close()
    logger.info("Database initialized successfully.")

def check_duplicate(product_id: str, site: str, minutes: int = 30) -> bool:
    """
    Checks if an alert was sent for the given product and site within the last `minutes` minutes.
    Returns True if a duplicate (should skip alert), False otherwise.
    """
    if not product_id or not site:
        return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    threshold_time = int(time.time()) - (minutes * 60)

    cursor.execute('''
        SELECT last_alert_time FROM alerts
        WHERE product_id = ? AND site = ?
    ''', (product_id, site))

    row = cursor.fetchone()
    conn.close()

    if row and row[0]:
        last_alert_time = row[0]
        if last_alert_time >= threshold_time:
            return True

    return False

def record_alert(product_id: str, site: str, price: float):
    """
    Records that an alert was sent. Inserts or updates the last_alert_time.
    """
    if not product_id or not site:
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    current_time = int(time.time())

    cursor.execute('''
        INSERT INTO alerts (product_id, site, price, timestamp, last_alert_time)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(product_id, site)
        DO UPDATE SET price=excluded.price, timestamp=excluded.timestamp, last_alert_time=excluded.last_alert_time
    ''', (product_id, site, price, current_time, current_time))

    conn.commit()
    conn.close()

def record_price_history(product_id: str, site: str, price: float):
    """
    Records a price point in history for the given product.
    """
    if not product_id or not site:
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    current_time = int(time.time())

    cursor.execute('''
        INSERT INTO price_history (product_id, site, price, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (product_id, site, price, current_time))

    conn.commit()
    conn.close()

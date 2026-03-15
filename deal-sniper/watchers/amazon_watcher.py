import re
import time
import random
import logging
from bs4 import BeautifulSoup
from parsers.deal_parser import extract_product_id

logger = logging.getLogger(__name__)

def rate_limit():
    """Implements rate limiting by sleeping for 2-5 seconds randomly."""
    delay = random.uniform(2, 5)
    time.sleep(delay)

def execute_with_retry(fetch_func, max_retries=2):
    """
    Executes a fetching function with exponential backoff and max retries.
    Delay starts at 1 sec, then 2 sec.
    """
    for attempt in range(max_retries + 1):
        try:
            return fetch_func()
        except Exception as e:
            if attempt == max_retries:
                logger.error(f"Failed after {max_retries} retries: {e}")
                return None
            else:
                delay = 2 ** attempt
                logger.warning(f"Request failed, retrying in {delay}s... ({e})")
                time.sleep(delay)
    return None

def fetch_product_data(url: str, session) -> dict:
    """
    Standard watcher interface for Amazon.
    """
    def do_fetch():
        rate_limit()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Accept-Language": "en-IN,en;q=0.9",
            "Connection": "keep-alive"
        }

        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Product Name
        title_elem = soup.find(id='productTitle')
        product_name = title_elem.get_text(strip=True) if title_elem else "Unknown Amazon Product"

        # Price Check (Multiple selectors based on spec)
        price = 0.0
        price_selectors = [
            soup.select_one('span.a-price-whole'),
            soup.select_one('span#priceblock_ourprice'),
            soup.select_one('span#priceblock_dealprice'),
            soup.select_one('span.a-color-price')
        ]

        for p in price_selectors:
            if p:
                text = p.get_text(strip=True)
                clean_text = re.sub(r'[^\d.]', '', text.replace(',', ''))
                if clean_text:
                    try:
                        price = float(clean_text)
                        break
                    except ValueError:
                        pass

        # MRP Check
        mrp = price
        mrp_elem = soup.select_one('span.a-text-price span.a-offscreen')
        if not mrp_elem:
            mrp_elem = soup.select_one('span.basisPrice span.a-offscreen')

        if mrp_elem:
            text = mrp_elem.get_text(strip=True)
            clean_text = re.sub(r'[^\d.]', '', text.replace(',', ''))
            if clean_text:
                try:
                    mrp = float(clean_text)
                except ValueError:
                    pass

        product_id = extract_product_id(url, 'amazon')

        return {
            "product_id": product_id,
            "product_name": product_name,
            "price": price,
            "mrp": max(price, mrp),
            "site": "amazon",
            "url": url
        }

    return execute_with_retry(do_fetch)

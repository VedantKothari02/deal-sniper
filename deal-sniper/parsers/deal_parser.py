import re
import logging
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)

def detect_site(url: str) -> str:
    domain = urlparse(url).netloc.lower()
    if 'amazon' in domain:
        return 'amazon'
    if 'flipkart' in domain:
        return 'flipkart'
    if 'myntra' in domain:
        return 'myntra'
    if 'ajio' in domain:
        return 'ajio'
    return 'unknown'

def normalize_url(url: str, site: str) -> str:
    """Removes tracking parameters to create a consistent URL."""
    try:
        parsed = urlparse(url)
        if site == 'amazon':
            # Extract ASIN and rebuild URL
            match = re.search(r'/dp/([A-Z0-9]+)', parsed.path)
            if match:
                return f"https://www.amazon.in/dp/{match.group(1)}"
        elif site == 'flipkart':
            # Extract PID and rebuild URL
            qs = parse_qs(parsed.query)
            pid = qs.get('pid', [None])[0]
            if pid:
                return f"https://www.flipkart.com{parsed.path}?pid={pid}"
        # For Myntra/Ajio or unknown, just strip the query params to normalize mostly
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    except Exception as e:
        logger.warning(f"Failed to normalize url {url}: {e}")
    return url

def extract_product_id(url: str, site: str) -> str:
    """Extracts a unique identifier based on the site."""
    try:
        if site == 'amazon':
            match = re.search(r'/dp/([A-Z0-9]+)', url)
            return match.group(1) if match else url
        if site == 'flipkart':
            qs = parse_qs(urlparse(url).query)
            pid = qs.get('pid', [None])[0]
            return pid if pid else url
    except Exception as e:
        logger.warning(f"Failed to extract product ID from {url}: {e}")
    return url

def parse_deal(text: str, url: str) -> dict:
    """
    Parses initial deal information from telegram text and link.
    Returns:
    {
        "product_name": str,
        "price": float,
        "mrp": float,
        "discount": float,
        "site": str,
        "product_id": str,
        "url": str
    }
    """
    site = detect_site(url)
    normalized_url = normalize_url(url, site)
    product_id = extract_product_id(normalized_url, site)

    # We attempt to guess price and MRP from text using simple regex
    # e.g., "Rs 599", "₹ 599", "599/-"
    price = 0.0
    mrp = 0.0
    discount = 0.0

    # Simple heuristic to find currency numbers
    amounts = re.findall(r'(?:₹|rs\.?|inr)?\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:/-)?', text, re.IGNORECASE)
    # Filter to actual numbers and convert to float
    parsed_amounts = []
    for a in amounts:
        try:
            val = float(a.replace(',', ''))
            parsed_amounts.append(val)
        except ValueError:
            pass

    # Assuming lower amount is price, higher is MRP if two exist
    if len(parsed_amounts) >= 2:
        parsed_amounts.sort()
        price = parsed_amounts[0]
        mrp = parsed_amounts[-1]
    elif len(parsed_amounts) == 1:
        price = parsed_amounts[0]
        mrp = price

    if mrp > 0:
        discount = round(((mrp - price) / mrp) * 100, 2)

    # Attempt to extract product name from first line or text snippet
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    product_name = lines[0] if lines else "Unknown Product"

    return {
        "product_name": product_name,
        "price": price,
        "mrp": mrp,
        "discount": discount,
        "site": site,
        "product_id": product_id,
        "url": normalized_url
    }

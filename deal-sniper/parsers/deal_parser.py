import re
import logging
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)


DEAL_KEYWORDS = [
    "loot",
    "combo loot",
    "grab",
    "grab fast",
    "price error",
    "glitch",
    "steal deal",
    "deal",
]


def detect_site(url: str) -> str:
    domain = urlparse(url).netloc.lower()

    if "amazon" in domain or "amzn" in domain:
        return "amazon"
    if "flipkart" in domain or "fkrt" in domain or "fktr" in domain or "fk" in domain:
        return "flipkart"
    if "myntra" in domain or "myntr" in domain:
        return "myntra"
    if "ajio" in domain or "ajiio" in domain:
        return "ajio"

    return "unknown"


def normalize_url(url: str, site: str) -> str:
    try:
        parsed = urlparse(url)

        if site == "amazon":
            match = re.search(r"/dp/([A-Z0-9]+)", parsed.path)
            if match:
                return f"https://www.amazon.in/dp/{match.group(1)}"

        elif site == "flipkart":
            qs = parse_qs(parsed.query)
            pid = qs.get("pid", [None])[0]

            if not pid:
                # Some flipkart dl links look like dl.flipkart.com/dl/...pid=XXXXX or just have pid as part of query
                # but might not be cleanly parsed if there are query issues.
                # Also we should check if pid is in path, e.g. /p/XXXXX
                match = re.search(r"pid=([A-Z0-9a-z]+)", url)
                if match:
                    pid = match.group(1)
                else:
                    match = re.search(r"/p/([A-Z0-9a-z]+)", parsed.path)
                    if match:
                        pid = match.group(1)

            if pid:
                return f"https://www.flipkart.com/item/p/{pid}"

        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

    except Exception as e:
        logger.warning(f"Failed to normalize url {url}: {e}")

    return url


def extract_product_id(url: str, site: str) -> str:
    try:

        if site == "amazon":
            match = re.search(r"/dp/([A-Z0-9]+)", url)
            if match:
                return match.group(1)

        if site == "flipkart":

            match = re.search(r"pid=([A-Z0-9a-z]+)", url)
            if match:
                return match.group(1)

            match = re.search(r"/p/([A-Z0-9a-z]+)", url)
            if match:
                return match.group(1)

    except Exception as e:
        logger.warning(f"Failed to extract product ID from {url}: {e}")

    return url


def parse_deal(text: str, url: str) -> dict:

    site = detect_site(url)
    normalized_url = normalize_url(url, site)
    product_id = extract_product_id(normalized_url, site)

    price = 0.0
    mrp = 0.0
    discount = 0.0
    coupon_info = None
    deal_keywords_found = []

    text_lower = text.lower()

    # ---------------------------
    # Detect deal keywords
    # ---------------------------
    for keyword in DEAL_KEYWORDS:
        if keyword in text_lower:
            deal_keywords_found.append(keyword)

    # ---------------------------
    # Detect percentage discount
    # ---------------------------
    discount_match = re.search(r"(\d{1,3})\s*%\s*off", text, re.IGNORECASE)

    if discount_match:
        discount = float(discount_match.group(1))

    # ---------------------------
    # Detect price mentions
    # ---------------------------
    price_matches = re.findall(
        r"(?:₹|rs\.?|inr)\s*([\d,]+)",
        text,
        re.IGNORECASE,
    )

    parsed_amounts = []

    for p in price_matches:
        try:
            parsed_amounts.append(float(p.replace(",", "")))
        except:
            pass

    if len(parsed_amounts) >= 2:
        parsed_amounts.sort()
        price = parsed_amounts[0]
        mrp = parsed_amounts[-1]

    elif len(parsed_amounts) == 1:
        price = parsed_amounts[0]

    # Compute discount only if not already detected
    if discount == 0 and mrp > 0:
        discount = round(((mrp - price) / mrp) * 100, 2)

    # ---------------------------
    # Detect coupon / bank offers
    # ---------------------------
    coupon_match = re.search(
        r"(apply\s+.*?coupon|extra\s+.*?cashback|bank\s+offer)",
        text,
        re.IGNORECASE,
    )

    if coupon_match:
        coupon_info = coupon_match.group(0).strip()

    # ---------------------------
    # Product name detection
    # ---------------------------
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    raw_product_name = "Unknown Product"

    for line in lines:

        if "http" in line.lower():
            continue

        if len(line) < 8:
            continue

        # Skip lines that are just coupons
        if coupon_info and line.lower() in coupon_info.lower():
            continue

        raw_product_name = line
        break

    # Issue 4: Product Name Cleaning
    cleaned = re.sub(r'(?:Upto|Min|Flat|Extra)?\s*\d{1,3}\s*%\s*Off\s*(?:On|:)?\s*', '', raw_product_name, flags=re.IGNORECASE)
    cleaned = re.sub(r'(?:at|under|starts at|for)\s*(?:₹|Rs\.?|INR)\s*[\d,]+(?:\.\d+)?\s*', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'^[\W_]+', '', cleaned).strip()
    product_name = cleaned if cleaned else raw_product_name

    return {
        "product_name": product_name,
        "price": price,
        "mrp": mrp,
        "discount": discount,
        "coupon_info": coupon_info,
        "deal_keywords": deal_keywords_found,
        "site": site,
        "product_id": product_id,
        "url": normalized_url,
    }
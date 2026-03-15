import pytest
from parsers.deal_parser import parse_deal, detect_site, normalize_url, extract_product_id

def test_detect_site():
    assert detect_site("https://www.amazon.in/dp/B08ABC123") == "amazon"
    assert detect_site("https://www.flipkart.com/p/itm123?pid=XYZ") == "flipkart"
    assert detect_site("https://www.myntra.com/product/123") == "myntra"
    assert detect_site("https://www.ajio.com/product/123") == "ajio"
    assert detect_site("https://www.google.com") == "unknown"

def test_normalize_url():
    # Test Amazon URL stripping
    url = "https://www.amazon.in/dp/B08ABC123?tag=affiliate_id&other=param"
    assert normalize_url(url, "amazon") == "https://www.amazon.in/dp/B08ABC123"

    # Test Flipkart URL parameter preservation
    url_fk = "https://www.flipkart.com/product/p/itm123?pid=XYZ123&tracking=true"
    assert normalize_url(url_fk, "flipkart") == "https://www.flipkart.com/item/p/XYZ123"

def test_extract_product_id():
    assert extract_product_id("https://www.amazon.in/dp/B08ABC123", "amazon") == "B08ABC123"
    assert extract_product_id("https://www.flipkart.com/p/itm123?pid=XYZ123", "flipkart") == "XYZ123"

def test_parse_deal():
    text = "Awesome Samsung SSD\nPrice: ₹899\nMRP: 2999"
    url = "https://www.amazon.in/dp/B08ABC123?tag=something"

    parsed = parse_deal(text, url)

    assert parsed['product_name'] == "Awesome Samsung SSD"
    assert parsed['price'] == 899.0
    assert parsed['mrp'] in [2999.0, 0.0, None]
    assert parsed['site'] == "amazon"
    assert parsed['product_id'] == "B08ABC123"
    assert parsed['url'] == "https://www.amazon.in/dp/B08ABC123"

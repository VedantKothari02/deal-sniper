import re
import requests
import logging

logger = logging.getLogger(__name__)

URL_REGEX = re.compile(
    r'(https?://(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?://(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})',
    re.IGNORECASE
)

def extract_links(text: str) -> list:
    """
    Extracts URLs from a block of text, then expands any shortened links
    using an HTTP HEAD request with redirects enabled.
    """
    if not text:
        return []

    found_urls = URL_REGEX.findall(text)
    expanded_urls = []

    for url in found_urls:
        if "amzn.to" in url or "fkrt.it" in url or "bit.ly" in url:
            try:
                response = requests.head(url, allow_redirects=True, timeout=5)
                expanded_urls.append(response.url)
            except Exception as e:
                logger.warning(f"Failed to expand shortened URL {url}: {e}")
                expanded_urls.append(url)
        else:
            expanded_urls.append(url)

    return expanded_urls

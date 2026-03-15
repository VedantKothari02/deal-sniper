import pytest
from parsers.link_extractor import extract_links

def test_extract_links_basic():
    text = "Here is a link: https://www.amazon.in/dp/B08ABC123 and another one http://flipkart.com/someproduct"
    links = extract_links(text)
    assert len(links) == 2
    assert "https://www.amazon.in/dp/B08ABC123" in links
    assert "http://flipkart.com/someproduct" in links

def test_extract_links_no_links():
    text = "Just some text without any links."
    links = extract_links(text)
    assert len(links) == 0

def test_extract_links_shortened(monkeypatch):
    # Mock requests.head for testing shortened link expansion
    class MockResponse:
        def __init__(self, url):
            self.url = url

    def mock_head(url, *args, **kwargs):
        if "amzn.to" in url:
            return MockResponse("https://www.amazon.in/dp/B08ABC123")
        return MockResponse(url)

    import requests
    monkeypatch.setattr(requests, "head", mock_head)

    text = "Short link: https://amzn.to/short123"
    links = extract_links(text)
    assert len(links) == 1
    assert links[0] == "https://www.amazon.in/dp/B08ABC123"

import pytest
from unittest.mock import Mock, patch
from tools.web_scraper import scrape_webpage, validate_public_url


def test_url_validation_blocks_internal_hosts():
    with pytest.raises(ValueError):
        validate_public_url("http://localhost:8000")


def test_url_validation_requires_http():
    with pytest.raises(ValueError):
        validate_public_url("ftp://example.com/file")


def test_scraper_removes_non_content_elements():
    response = Mock(content=b"<html><title>News</title><nav>Menu</nav><main>Hello <b>world</b></main><script>bad()</script></html>", headers={})
    response.raise_for_status.return_value = None
    with patch("tools.web_scraper.requests.get", return_value=response):
        result = scrape_webpage.invoke({"url": "https://example.com", "max_chars": 1000})
    assert result["title"] == "News"
    assert result["text"] == "Hello world"


def test_scraper_propagates_http_errors():
    response = Mock()
    response.raise_for_status.side_effect = RuntimeError("HTTP error")
    response.headers = {}
    with patch("tools.web_scraper.requests.get", return_value=response), pytest.raises(RuntimeError, match="HTTP error"):
        scrape_webpage.invoke({"url": "https://example.com"})

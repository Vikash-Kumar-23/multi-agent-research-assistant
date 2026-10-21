from ipaddress import ip_address
from urllib.parse import urlparse
import socket
import requests
from bs4 import BeautifulSoup
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from config.settings import get_settings


class ScrapeInput(BaseModel):
    url: str = Field(description="Public HTTP or HTTPS URL to read")
    max_chars: int = Field(default=12000, ge=1000, le=50000)


def validate_public_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Only valid HTTP/HTTPS URLs are allowed.")
    host = parsed.hostname.lower()
    if host in {"localhost", "localhost.localdomain"} or host.endswith(".local"):
        raise ValueError("Internal hostnames are not allowed.")
    try:
        addresses = socket.getaddrinfo(host, None)
        for item in addresses:
            address = ip_address(item[4][0])
            if address.is_private or address.is_loopback or address.is_link_local or address.is_reserved:
                raise ValueError("Private or internal network destinations are not allowed.")
    except socket.gaierror as exc:
        raise ValueError("The hostname could not be resolved.") from exc


@tool(args_schema=ScrapeInput)
def scrape_webpage(url: str, max_chars: int = 12000) -> dict:
    """Fetch a public webpage, remove non-content HTML, and return clean text."""
    validate_public_url(url)
    settings = get_settings()
    response = requests.get(url, headers={"User-Agent": "ResearchAssistant/0.1 (+https://example.invalid/research)"}, timeout=settings.request_timeout, stream=True)
    response.raise_for_status()
    if int(response.headers.get("content-length", 0) or 0) > 5_000_000:
        raise ValueError("Response is too large to read safely.")
    content = response.content[:5_000_000]
    soup = BeautifulSoup(content, "html.parser")
    for element in soup(["script", "style", "nav", "footer", "header", "aside", "form", "noscript"]):
        element.decompose()
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    if soup.title:
        soup.title.decompose()
    text = " ".join(soup.get_text(" ").split())[:max_chars]
    if not text:
        raise ValueError("No readable page text was found.")
    return {"url": url, "title": title, "text": text}

"""Web scraping service – extracts text and metadata from URLs."""

from __future__ import annotations

import asyncio
import re
import time
from typing import Any
from urllib.parse import urlparse

import aiohttp
import requests
from bs4 import BeautifulSoup

from config import ScrapingConfig

_DEFAULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

_USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.2 Safari/605.1.15",
]

_ua_index = 0


def _next_ua() -> str:
    global _ua_index
    ua = _USER_AGENTS[_ua_index % len(_USER_AGENTS)]
    _ua_index += 1
    return ua


def _clean_text(text: str) -> str:
    """Remove excessive whitespace from scraped text."""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def scrape_url(url: str) -> dict[str, Any]:
    """
    Synchronously scrape a URL and return a structured result.

    Returns a dict with keys:
        url, title, text, meta_description, links, images, success, error
    """
    result: dict[str, Any] = {
        "url": url,
        "title": "",
        "text": "",
        "meta_description": "",
        "links": [],
        "images": [],
        "success": False,
        "error": None,
    }

    headers = dict(_DEFAULT_HEADERS)
    if ScrapingConfig.ROTATE_UA:
        headers["User-Agent"] = _next_ua()

    for attempt in range(ScrapingConfig.MAX_RETRIES):
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=ScrapingConfig.TIMEOUT,
                allow_redirects=True,
            )
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "")
            if "pdf" in content_type.lower():
                result["text"] = "[PDF file – use /analyze_pdf command to process it]"
                result["success"] = True
                return result

            soup = BeautifulSoup(response.text, "lxml")

            # Remove script / style noise
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()

            # Title
            title_tag = soup.find("title")
            result["title"] = title_tag.get_text(strip=True) if title_tag else ""

            # Meta description
            meta = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)})
            if meta:
                result["meta_description"] = meta.get("content", "")

            # Main text
            body = soup.find("body")
            if body:
                result["text"] = _clean_text(body.get_text(separator=" "))

            # Links (internal + external)
            base = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if href.startswith("http"):
                    result["links"].append(href)
                elif href.startswith("/"):
                    result["links"].append(base + href)

            # Images
            for img in soup.find_all("img", src=True):
                src = img["src"]
                if src.startswith("http"):
                    result["images"].append(src)

            result["success"] = True
            return result

        except requests.exceptions.RequestException as exc:
            result["error"] = str(exc)
            if attempt < ScrapingConfig.MAX_RETRIES - 1:
                time.sleep(ScrapingConfig.DELAY * (attempt + 1))

    return result


async def async_scrape_url(url: str) -> dict[str, Any]:
    """Async wrapper around scrape_url."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, scrape_url, url)


async def scrape_multiple(urls: list[str]) -> list[dict[str, Any]]:
    """Scrape multiple URLs concurrently."""
    tasks = [async_scrape_url(u) for u in urls]
    return await asyncio.gather(*tasks)

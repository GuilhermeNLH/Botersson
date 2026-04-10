"""Internet search service using DuckDuckGo (no API key required)."""

from __future__ import annotations

import asyncio
from typing import Any

from duckduckgo_search import DDGS

from config import SearchConfig


def search_web(query: str, max_results: int | None = None) -> list[dict[str, Any]]:
    """
    Search the web using DuckDuckGo.

    Returns a list of dicts with keys: title, href, body.
    """
    n = max_results or SearchConfig.MAX_RESULTS
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=n):
                results.append(
                    {
                        "title": r.get("title", ""),
                        "url": r.get("href", ""),
                        "snippet": r.get("body", ""),
                    }
                )
    except Exception as exc:  # noqa: BLE001
        results.append({"error": str(exc)})
    return results


def search_news(query: str, max_results: int | None = None) -> list[dict[str, Any]]:
    """Search recent news via DuckDuckGo news."""
    n = max_results or SearchConfig.MAX_RESULTS
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.news(query, max_results=n):
                results.append(
                    {
                        "title": r.get("title", ""),
                        "url": r.get("url", ""),
                        "snippet": r.get("body", ""),
                        "date": r.get("date", ""),
                        "source": r.get("source", ""),
                    }
                )
    except Exception as exc:  # noqa: BLE001
        results.append({"error": str(exc)})
    return results


async def async_search_web(query: str, max_results: int | None = None) -> list[dict[str, Any]]:
    """Async wrapper for search_web."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, search_web, query, max_results)


async def async_search_news(query: str, max_results: int | None = None) -> list[dict[str, Any]]:
    """Async wrapper for search_news."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, search_news, query, max_results)

"""Patent and academic article search service."""

from __future__ import annotations

import asyncio
import re
from typing import Any
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

from config import ScrapingConfig

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
}


# ─── Google Patents ──────────────────────────────────────────────────────────

def search_google_patents(query: str, max_results: int = 10) -> list[dict[str, Any]]:
    """
    Scrape Google Patents search results for a given query.
    Returns list of patent dicts: title, patent_id, url, abstract, assignee, date.
    """
    url = f"https://patents.google.com/xhr/query?url=q%3D{quote(query)}&o=0&rs={max_results}"
    results = []
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=ScrapingConfig.TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        for item in data.get("results", {}).get("cluster", [{}])[0].get("result", []):
            patent = item.get("patent", {})
            results.append(
                {
                    "type": "patent",
                    "title": patent.get("title", ""),
                    "patent_id": patent.get("publication_number", ""),
                    "url": f"https://patents.google.com/patent/{patent.get('publication_number', '')}",
                    "abstract": patent.get("abstract", ""),
                    "assignee": ", ".join(patent.get("assignee", [])),
                    "date": patent.get("publication_date", ""),
                    "inventor": ", ".join(patent.get("inventor", [])),
                }
            )
    except Exception as exc:  # noqa: BLE001
        results.append({"error": str(exc), "type": "patent"})
    return results


def scrape_patent_detail(patent_url: str) -> dict[str, Any]:
    """Scrape the full text of a Google Patent page."""
    result: dict[str, Any] = {
        "type": "patent",
        "url": patent_url,
        "title": "",
        "abstract": "",
        "claims": "",
        "description": "",
        "success": False,
        "error": None,
    }
    try:
        resp = requests.get(patent_url, headers=_HEADERS, timeout=ScrapingConfig.TIMEOUT)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        title_el = soup.find("h1", id="title")
        if title_el:
            result["title"] = title_el.get_text(strip=True)

        abstract_el = soup.find("div", class_="abstract")
        if abstract_el:
            result["abstract"] = abstract_el.get_text(separator=" ", strip=True)

        claims_el = soup.find("section", itemprop="claims")
        if claims_el:
            result["claims"] = claims_el.get_text(separator="\n", strip=True)

        desc_el = soup.find("section", itemprop="description")
        if desc_el:
            result["description"] = desc_el.get_text(separator=" ", strip=True)[:5000]

        result["success"] = True
    except Exception as exc:  # noqa: BLE001
        result["error"] = str(exc)
    return result


# ─── Semantic Scholar / arXiv ────────────────────────────────────────────────

def search_semantic_scholar(query: str, max_results: int = 10) -> list[dict[str, Any]]:
    """Search Semantic Scholar for academic articles (free API, no key needed)."""
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": max_results,
        "fields": "title,abstract,authors,year,url,externalIds,publicationTypes",
    }
    results = []
    try:
        resp = requests.get(url, params=params, timeout=ScrapingConfig.TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        for paper in data.get("data", []):
            authors = [a.get("name", "") for a in paper.get("authors", [])]
            doi = paper.get("externalIds", {}).get("DOI", "")
            arxiv_id = paper.get("externalIds", {}).get("ArXiv", "")
            paper_url = paper.get("url", "")
            if arxiv_id:
                paper_url = f"https://arxiv.org/abs/{arxiv_id}"
            results.append(
                {
                    "type": "article",
                    "title": paper.get("title", ""),
                    "abstract": paper.get("abstract", "") or "",
                    "authors": ", ".join(authors),
                    "year": paper.get("year", ""),
                    "doi": doi,
                    "url": paper_url,
                    "publication_types": paper.get("publicationTypes", []),
                }
            )
    except Exception as exc:  # noqa: BLE001
        results.append({"error": str(exc), "type": "article"})
    return results


def search_arxiv(query: str, max_results: int = 10) -> list[dict[str, Any]]:
    """Search arXiv preprints via their public API."""
    url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max_results,
    }
    results = []
    try:
        resp = requests.get(url, params=params, timeout=ScrapingConfig.TIMEOUT)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "xml")
        for entry in soup.find_all("entry"):
            authors = [a.find("name").get_text() for a in entry.find_all("author") if a.find("name")]
            results.append(
                {
                    "type": "article",
                    "title": (entry.find("title") or {}).get_text(strip=True) if entry.find("title") else "",
                    "abstract": (entry.find("summary") or {}).get_text(strip=True) if entry.find("summary") else "",
                    "authors": ", ".join(authors),
                    "url": (entry.find("id") or {}).get_text(strip=True) if entry.find("id") else "",
                    "published": (entry.find("published") or {}).get_text(strip=True) if entry.find("published") else "",
                    "source": "arXiv",
                }
            )
    except Exception as exc:  # noqa: BLE001
        results.append({"error": str(exc), "type": "article"})
    return results


# ─── Async wrappers ──────────────────────────────────────────────────────────

async def async_search_patents(query: str, max_results: int = 10) -> list[dict[str, Any]]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, search_google_patents, query, max_results)


async def async_scrape_patent(url: str) -> dict[str, Any]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, scrape_patent_detail, url)


async def async_search_articles(query: str, max_results: int = 10) -> list[dict[str, Any]]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, search_semantic_scholar, query, max_results)


async def async_search_arxiv(query: str, max_results: int = 10) -> list[dict[str, Any]]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, search_arxiv, query, max_results)

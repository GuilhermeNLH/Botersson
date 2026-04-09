"""Botersson Web GUI – Flask application."""

from __future__ import annotations

import io
import ipaddress
import json
import logging
import sys
from pathlib import Path
from urllib.parse import urlparse

from flask import Flask, jsonify, render_template, request, send_file, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bot.services import excel_manager, llm, patent_search, scraper, search_engine
from config import WebConfig

log = logging.getLogger(__name__)

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = WebConfig.SECRET_KEY
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# ─── URL validation helper ────────────────────────────────────────────────────

_ALLOWED_SCHEMES = {"http", "https"}


def _validate_url(url: str) -> str | None:
    """
    Validate a user-supplied URL.
    Returns the URL string if valid, or None if it should be rejected.

    Rejects:
    - Non-http/https schemes (file://, ftp://, javascript://, etc.)
    - URLs with no hostname
    - URLs resolving to private, loopback, link-local, or reserved IP ranges
      (uses the ipaddress stdlib module to cover all RFC-1918 / RFC-4193 ranges)
    """
    if not url:
        return None
    try:
        parsed = urlparse(url)
        # Access port to catch malformed URLs like http://fc00::1 (bare IPv6)
        _ = parsed.port
    except (Exception, ValueError):
        return None
    if parsed.scheme not in _ALLOWED_SCHEMES:
        return None
    if not parsed.netloc:
        return None

    hostname = parsed.hostname
    # Reject missing hostname (e.g. bare IPv6 without brackets)
    if not hostname:
        return None
    # Reject plain "localhost"
    if hostname.lower() == "localhost":
        return None

    # If the hostname looks like an IP address, check for private/reserved ranges
    try:
        ip = ipaddress.ip_address(hostname)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            return None
    except ValueError:
        # Not an IP address – hostname-based, allow it (DNS resolution happens later)
        pass

    return url

# ─── Pages ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Main dashboard."""
    summary = excel_manager.get_all_sheets_summary()
    models = llm.list_ollama_models()
    return render_template("index.html", summary=summary, models=models)


@app.route("/excel")
def excel_page():
    """Excel database management page."""
    sheets = list(excel_manager.SHEET_COLUMNS.keys())
    active_sheet = request.args.get("sheet", "Articles")
    data = excel_manager.get_sheet_data(active_sheet)
    columns = excel_manager.SHEET_COLUMNS.get(active_sheet, [])
    return render_template(
        "excel.html",
        sheets=sheets,
        active_sheet=active_sheet,
        columns=columns,
        data=data,
    )


@app.route("/settings")
def settings_page():
    """Settings / configuration page."""
    from config import BotConfig, OllamaConfig, SchedulerConfig
    models = llm.list_ollama_models()
    return render_template(
        "settings.html",
        ollama_host=OllamaConfig.HOST,
        ollama_model=OllamaConfig.MODEL,
        available_models=models,
        daily_hour=SchedulerConfig.DAILY_HOUR,
    )


# ─── REST API ─────────────────────────────────────────────────────────────────

@app.route("/api/summary")
def api_summary():
    return jsonify(excel_manager.get_all_sheets_summary())


@app.route("/api/sheet/<sheet_name>")
def api_sheet(sheet_name: str):
    data = excel_manager.get_sheet_data(sheet_name)
    return jsonify(data)


@app.route("/api/chart")
def api_chart():
    chart_type = request.args.get("type", "bar")
    topic = request.args.get("topic", "")
    buf = excel_manager.generate_chart(chart_type=chart_type, topic=topic)
    return send_file(buf, mimetype="image/png", download_name="chart.png")


@app.route("/api/themes_chart")
def api_themes_chart():
    topic = request.args.get("topic", "")
    buf = excel_manager.generate_themes_chart(topic=topic)
    return send_file(buf, mimetype="image/png", download_name="themes.png")


@app.route("/api/search", methods=["POST"])
def api_search():
    data = request.json or {}
    query = data.get("query", "")
    search_type = data.get("type", "web")  # web | patent | article | arxiv | news
    # Clamp max_results to a safe range
    try:
        max_results = max(1, min(int(data.get("max_results", 10)), 50))
    except (TypeError, ValueError):
        max_results = 10

    if not query:
        return jsonify({"error": "query is required"}), 400

    if search_type == "patent":
        results = patent_search.search_google_patents(query, max_results)
    elif search_type == "article":
        results = patent_search.search_semantic_scholar(query, max_results)
    elif search_type == "arxiv":
        results = patent_search.search_arxiv(query, max_results)
    elif search_type == "news":
        results = search_engine.search_news(query, max_results)
    else:
        results = search_engine.search_web(query, max_results)

    # Save to DB (skip error entries); strip internal error details from response
    sanitized = []
    for r in results:
        if "error" in r:
            sanitized.append({"error": "Search request failed. Please try again."})
        else:
            excel_manager.save_search_result(r, query)
            sanitized.append(r)

    return jsonify(sanitized)


@app.route("/api/scrape", methods=["POST"])
def api_scrape():
    data = request.json or {}
    raw_url = data.get("url", "")
    url = _validate_url(raw_url)
    if not url:
        return jsonify({"error": "A valid http/https URL is required"}), 400
    result = scraper.scrape_url(url)
    # Return only safe fields – never expose raw exception messages
    safe = {
        "url": result.get("url", ""),
        "title": result.get("title", ""),
        "text": result.get("text", ""),
        "meta_description": result.get("meta_description", ""),
        "success": result.get("success", False),
    }
    if not safe["success"]:
        safe["error"] = "Could not retrieve the page. Check that the URL is accessible."
    return jsonify(safe)


@app.route("/api/classify", methods=["POST"])
def api_classify():
    data = request.json or {}
    text = data.get("text", "")
    title = data.get("title", "")
    topic = data.get("topic", "")
    if not text or not topic:
        return jsonify({"error": "text and topic are required"}), 400
    classification = llm.classify_content(text, title, topic)
    return jsonify(classification)


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    """Full pipeline: scrape URL → classify with AI → save to Excel."""
    data = request.json or {}
    raw_url = data.get("url", "")
    topic = data.get("topic", "research")
    content_type = data.get("content_type", "auto")  # auto | article | patent

    url = _validate_url(raw_url)
    if not url:
        return jsonify({"error": "A valid http/https URL is required"}), 400

    # Scrape
    scraped = scraper.scrape_url(url)
    if not scraped.get("success"):
        return jsonify({"error": "Could not retrieve the page. Check that the URL is accessible."}), 422

    text = scraped.get("text", "")
    title = scraped.get("title", "")

    # Classify
    classification = llm.classify_content(text, title, topic)

    # Detect content type
    if content_type == "auto":
        content_type = classification.get("content_type", "article")

    # Save
    item = {
        "title": title,
        "url": url,
        "abstract": scraped.get("meta_description", text[:500]),
        "authors": "",
        "year": "",
        "doi": "",
        "patent_id": "",
        "assignee": "",
        "inventor": "",
        "date": "",
    }
    if content_type == "patent":
        row_id = excel_manager.save_patent(item, classification)
        sheet = "Patents"
    else:
        row_id = excel_manager.save_article(item, classification)
        sheet = "Articles"

    return jsonify(
        {
            "success": True,
            "sheet": sheet,
            "id": row_id,
            "title": title,
            "classification": classification,
        }
    )


@app.route("/api/add_theme", methods=["POST"])
def api_add_theme():
    data = request.json or {}
    theme_type = data.get("type", "macro")
    theme = data.get("theme", "")
    parent = data.get("parent", "")
    description = data.get("description", "")
    if not theme:
        return jsonify({"error": "theme is required"}), 400
    row_id = excel_manager.save_theme(theme_type, theme, parent, description)
    return jsonify({"id": row_id, "message": f"Theme saved"})


@app.route("/api/export_excel")
def api_export_excel():
    """Download the Excel file."""
    path = excel_manager.workbook_path()
    if not path.exists():
        excel_manager.ensure_workbook()
    return send_file(str(path), as_attachment=True, download_name=path.name)


@app.route("/api/models")
def api_models():
    return jsonify({"models": llm.list_ollama_models()})


# ─── SocketIO events ──────────────────────────────────────────────────────────

@socketio.on("search")
def socket_search(data):
    query = data.get("query", "")
    search_type = data.get("type", "web")
    results = search_engine.search_web(query) if search_type == "web" else []
    emit("search_results", {"results": results})


@socketio.on("analyze")
def socket_analyze(data):
    raw_url = data.get("url", "")
    url = _validate_url(raw_url)
    if not url:
        emit("analyze_result", {"error": "A valid http/https URL is required"})
        return
    topic = data.get("topic", "research")
    scraped = scraper.scrape_url(url)
    if not scraped.get("success"):
        emit("analyze_result", {"error": "Could not retrieve the page."})
        return
    classification = llm.classify_content(scraped.get("text", ""), scraped.get("title", ""), topic)
    emit("analyze_result", {"success": True, "classification": classification, "title": scraped.get("title")})


# ─── Launch ───────────────────────────────────────────────────────────────────

def run_web() -> None:
    socketio.run(app, host=WebConfig.HOST, port=WebConfig.PORT, debug=WebConfig.DEBUG)


if __name__ == "__main__":
    run_web()

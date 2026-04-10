"""MCP (Model Context Protocol) server for Botersson.

Exposes research tools as MCP tools so that any MCP-compatible client
(Claude Desktop, Cursor, etc.) can control the bot and its Excel database.
"""

from __future__ import annotations

import asyncio
import json
import logging
import threading
from typing import Any

log = logging.getLogger(__name__)

# ─── Try to import the MCP library ───────────────────────────────────────────
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        CallToolResult,
        ListToolsResult,
        TextContent,
        Tool,
    )
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    log.warning("mcp package not installed – MCP server disabled. Install with: pip install mcp")


# ─── Tool definitions ────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "search_web",
        "description": "Search the internet for research information.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "max_results": {"type": "integer", "description": "Maximum results", "default": 10},
            },
            "required": ["query"],
        },
    },
    {
        "name": "search_patents",
        "description": "Search Google Patents for patents related to a topic.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Patent search query"},
                "max_results": {"type": "integer", "default": 10},
            },
            "required": ["query"],
        },
    },
    {
        "name": "search_articles",
        "description": "Search Semantic Scholar for academic articles.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "max_results": {"type": "integer", "default": 10},
            },
            "required": ["query"],
        },
    },
    {
        "name": "scrape_url",
        "description": "Extract text content from a URL (webpage, article, patent page).",
        "input_schema": {
            "type": "object",
            "properties": {"url": {"type": "string"}},
            "required": ["url"],
        },
    },
    {
        "name": "classify_content",
        "description": "Use local LLM to classify content into macro/meso/micro themes.",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "title": {"type": "string", "default": ""},
                "topic": {"type": "string", "description": "Research topic context"},
            },
            "required": ["text", "topic"],
        },
    },
    {
        "name": "save_article",
        "description": "Save an article to the Excel research database.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "authors": {"type": "string"},
                "year": {"type": "string"},
                "doi": {"type": "string"},
                "url": {"type": "string"},
                "abstract": {"type": "string"},
            },
            "required": ["title"],
        },
    },
    {
        "name": "save_patent",
        "description": "Save a patent to the Excel research database.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "patent_id": {"type": "string"},
                "assignee": {"type": "string"},
                "url": {"type": "string"},
                "abstract": {"type": "string"},
            },
            "required": ["title"],
        },
    },
    {
        "name": "get_database_summary",
        "description": "Get a summary of all data in the Excel research database.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_sheet_data",
        "description": "Get all rows from a specific sheet in the Excel database.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sheet_name": {
                    "type": "string",
                    "enum": ["Macro Themes", "Meso Themes", "Micro Themes", "Articles", "Patents", "Search Results"],
                }
            },
            "required": ["sheet_name"],
        },
    },
    {
        "name": "list_ollama_models",
        "description": "List all locally available Ollama models.",
        "input_schema": {"type": "object", "properties": {}},
    },
]


# ─── Tool executor ────────────────────────────────────────────────────────────

async def _execute_tool(name: str, arguments: dict[str, Any]) -> Any:
    """Execute a named MCP tool and return the result."""
    from bot.services import (
        excel_manager,
        llm,
        patent_search,
        scraper,
        search_engine,
    )

    if name == "search_web":
        return await search_engine.async_search_web(
            arguments["query"], arguments.get("max_results", 10)
        )

    elif name == "search_patents":
        return await patent_search.async_search_patents(
            arguments["query"], arguments.get("max_results", 10)
        )

    elif name == "search_articles":
        return await patent_search.async_search_articles(
            arguments["query"], arguments.get("max_results", 10)
        )

    elif name == "scrape_url":
        result = await scraper.async_scrape_url(arguments["url"])
        return {"title": result.get("title"), "text": result.get("text", "")[:3000]}

    elif name == "classify_content":
        return await llm.async_classify(
            arguments["text"],
            arguments.get("title", ""),
            arguments["topic"],
        )

    elif name == "save_article":
        row_id = excel_manager.save_article(arguments)
        return {"id": row_id, "message": f"Article saved with ID {row_id}"}

    elif name == "save_patent":
        row_id = excel_manager.save_patent(arguments)
        return {"id": row_id, "message": f"Patent saved with ID {row_id}"}

    elif name == "get_database_summary":
        return excel_manager.get_all_sheets_summary()

    elif name == "get_sheet_data":
        return excel_manager.get_sheet_data(arguments["sheet_name"])

    elif name == "list_ollama_models":
        models = llm.list_ollama_models()
        return {"models": models}

    return {"error": f"Unknown tool: {name}"}


# ─── MCP Server ───────────────────────────────────────────────────────────────

async def run_mcp_server() -> None:
    """Run the MCP stdio server (used by Claude Desktop / Cursor integration)."""
    if not MCP_AVAILABLE:
        log.error("Cannot start MCP server: mcp package not installed.")
        return

    app = Server("botersson")

    @app.list_tools()
    async def handle_list_tools() -> ListToolsResult:
        return ListToolsResult(
            tools=[
                Tool(
                    name=t["name"],
                    description=t["description"],
                    inputSchema=t["input_schema"],
                )
                for t in TOOLS
            ]
        )

    @app.call_tool()
    async def handle_call_tool(name: str, arguments: dict[str, Any]) -> CallToolResult:
        try:
            result = await _execute_tool(name, arguments)
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
            )
        except Exception as exc:  # noqa: BLE001
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps({"error": str(exc)}))]
            )

    log.info("Starting Botersson MCP server (stdio mode)...")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


def start_mcp_server_thread() -> threading.Thread | None:
    """Launch the MCP server in a background thread (for use alongside the bot)."""
    if not MCP_AVAILABLE:
        return None

    def _run() -> None:
        try:
            asyncio.run(run_mcp_server())
        except Exception as exc:  # noqa: BLE001
            log.error("MCP server error: %s", exc)

    t = threading.Thread(target=_run, daemon=True, name="mcp-server")
    t.start()
    return t

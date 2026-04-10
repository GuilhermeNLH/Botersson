#!/usr/bin/env python3
"""
Botersson – unified launcher.

Usage:
    python run.py            # Start both bot and web GUI
    python run.py --bot      # Discord bot only
    python run.py --web      # Web GUI only
    python run.py --mcp      # MCP stdio server only (for Claude Desktop / Cursor)
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
import threading
from pathlib import Path

# Ensure root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s – %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("botersson.run")


def start_web_server() -> threading.Thread:
    from web.app import run_web
    t = threading.Thread(target=run_web, daemon=True, name="web-gui")
    t.start()
    log.info("Web GUI started on http://localhost:5000")
    return t


async def start_bot() -> None:
    from bot.main import main as bot_main
    await bot_main()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Botersson launcher")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--bot", action="store_true", help="Discord bot only")
    group.add_argument("--web", action="store_true", help="Web GUI only")
    group.add_argument("--mcp", action="store_true", help="MCP stdio server only")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.web:
        log.info("Starting Web GUI only…")
        from web.app import run_web
        run_web()
        return

    if args.mcp:
        log.info("Starting MCP server (stdio mode)…")
        from bot.services.mcp_server import run_mcp_server
        asyncio.run(run_mcp_server())
        return

    if args.bot:
        log.info("Starting Discord bot only…")
        asyncio.run(start_bot())
        return

    # Default: start web GUI in background thread, then run the bot
    log.info("Starting Botersson (bot + web GUI)…")
    start_web_server()
    asyncio.run(start_bot())


if __name__ == "__main__":
    main()

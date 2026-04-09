"""MCP server entry point – allows running as `python -m bot.services.mcp_server`."""

from bot.services.mcp_server import run_mcp_server
import asyncio

if __name__ == "__main__":
    asyncio.run(run_mcp_server())

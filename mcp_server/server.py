"""
ADME Predictor MCP Server entry point.

Supports stdio transport (local use with Claude Desktop / Cursor).
HTTP/SSE transport will be added in Phase 3.

Install:
    pip install adme-predictor-mcp
    # or
    uvx adme-predictor-mcp

Claude Desktop config (~/.claude/claude_desktop_config.json):
    {
      "mcpServers": {
        "adme-predictor": {
          "command": "uvx",
          "args": ["adme-predictor-mcp"]
        }
      }
    }
"""

from __future__ import annotations

from mcp.server import Server
from mcp.server.stdio import stdio_server

from mcp_server.tools import register_tools

server = Server("adme-predictor")
register_tools(server)


def main() -> None:
    import asyncio

    async def run():
        async with stdio_server() as streams:
            await server.run(*streams, server.create_initialization_options())

    asyncio.run(run())


if __name__ == "__main__":
    main()

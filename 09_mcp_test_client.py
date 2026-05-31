"""Test MCP server trực tiếp — không cần Claude Code"""
import asyncio, sys
sys.stdout.reconfigure(encoding="utf-8")

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_mcp_server():
    server_params = StdioServerParameters(
        command="python",
        args=["C:/Users/letha/OneDrive/Documents/Vlance/anthropic-academy/09_mcp_server.py"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Lấy danh sách tools
            tools = await session.list_tools()
            print("Tools có sẵn:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")

            # Gọi tool get_pricing
            print("\nGọi get_pricing(web):")
            result = await session.call_tool("get_pricing", {"service": "web"})
            print(f"  {result.content[0].text}")

            print("\nGọi check_availability:")
            result = await session.call_tool("check_availability", {})
            print(f"  {result.content[0].text}")

asyncio.run(test_mcp_server())

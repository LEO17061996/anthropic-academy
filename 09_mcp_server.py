import asyncio, sys
sys.stdout.reconfigure(encoding="utf-8")

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Tạo MCP server tên "leo-studio"
app = Server("leo-studio")

# --- Định nghĩa Tools ---

@app.list_tools()
async def list_tools() -> list[Tool]:
    """Claude hỏi server có tool gì → trả về danh sách"""
    return [
        Tool(
            name="get_pricing",
            description="Lấy bảng giá dịch vụ Leo Studio",
            inputSchema={
                "type": "object",
                "properties": {
                    "service": {
                        "type": "string",
                        "description": "Tên dịch vụ: 'web', 'logo', hoặc 'all'"
                    }
                },
                "required": ["service"]
            }
        ),
        Tool(
            name="check_availability",
            description="Kiểm tra Leo Studio có nhận dự án mới không",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Claude gọi tool → chạy logic thật → trả kết quả"""

    if name == "get_pricing":
        service = arguments.get("service", "all")
        pricing = {
            "web":  "Thiết kế web: 5-15 triệu (landing: 5tr, chuẩn: 10tr, phức tạp: 15tr)",
            "logo": "Thiết kế logo: 2-5 triệu (3 concept, 2 lần sửa, file AI/PNG/SVG)",
        }
        if service == "all":
            result = "\n".join(pricing.values())
        else:
            result = pricing.get(service, "Dịch vụ không tồn tại")

        return [TextContent(type="text", text=result)]

    elif name == "check_availability":
        # Thực tế: query database xem lịch có trống không
        return [TextContent(type="text", text="Leo Studio đang nhận dự án mới. Thời gian bắt đầu sớm nhất: tuần tới.")]

    return [TextContent(type="text", text=f"Tool '{name}' không tồn tại")]

# --- Chạy server ---
async def main():
    print("Leo Studio MCP Server đang chạy...", file=sys.stderr)
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())

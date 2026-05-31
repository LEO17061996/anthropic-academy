# Anthropic Academy — Building with Claude API

Hands-on learning repo: Claude API từ cơ bản đến MCP server.  
Stack: Python 3.11 + Anthropic SDK 0.105+

---

## Modules

| File | Module | Concept |
|------|--------|---------|
| `01_hello_claude.py` | 2 | First API call |
| `02_system_prompt.py` | 2 | System prompt — định vai Claude |
| `03_multi_turn.py` | 2 | Multi-turn conversation |
| `04_streaming.py` | 2 | Streaming response |
| `05_prompt_eval.py` | 3 | Prompt evaluation (code + model grading) |
| `06_tool_use.py` | 5 | Tool Use — kết nối AI với dữ liệu thật |
| `07_rag_basic.py` | 6 | RAG — retrieval-augmented generation |
| `08_prompt_caching.py` | 7 | Prompt caching — giảm cost 90% |
| `09_mcp_server.py` | 8 | MCP server — leo-studio tools |
| `09_mcp_test_client.py` | 8 | MCP client test |

---

## MCP Server: leo-studio

Custom MCP server cho Leo Studio với 2 tools:

- **`get_pricing`** — Lấy bảng giá dịch vụ (web / logo)
- **`check_availability`** — Kiểm tra lịch nhận dự án

### Cài đặt

```bash
pip install anthropic mcp
```

### Chạy MCP server

```bash
python 09_mcp_server.py
```

### Test trực tiếp

```bash
python 09_mcp_test_client.py
```

### Kết nối vào Claude Code

Thêm vào `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "leo-studio": {
      "command": "python",
      "args": ["/path/to/09_mcp_server.py"]
    }
  }
}
```

---

## Setup

```bash
pip install anthropic mcp
export ANTHROPIC_API_KEY=sk-ant-...
python 01_hello_claude.py
```

---

## Key Learnings

- **System prompt** kiểm soát hoàn toàn hành vi Claude
- **Claude không tự nhớ** — phải tự giữ conversation history
- **Tool Use** = AI kết nối dữ liệu thật của doanh nghiệp
- **RAG** = AI đọc tài liệu nội bộ, không bịa thông tin
- **Prompt Caching** = giảm 90% cost với system prompt dài
- **MCP** = chuẩn kết nối chung, viết 1 lần dùng được mọi AI

---

Built by [Leo](https://leo-studio.pages.dev) — Senior AI-Native Developer path 2026

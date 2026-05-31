import anthropic, sys
sys.stdout.reconfigure(encoding="utf-8")

client = anthropic.Anthropic()

# Bước 1: Định nghĩa tool
tools = [{
    "name": "tinh_gia",
    "description": "Tính giá dịch vụ Leo Studio. Dùng khi khách hỏi về giá web hoặc logo.",
    "input_schema": {
        "type": "object",
        "properties": {
            "dich_vu": {
                "type": "string",
                "description": "Loại dịch vụ: 'web' hoặc 'logo'"
            },
            "do_phuc_tap": {
                "type": "string",
                "description": "Độ phức tạp: 'don_gian', 'trung_binh', 'phuc_tap'"
            }
        },
        "required": ["dich_vu", "do_phuc_tap"]
    }
}]

# Bước 2: Hàm Python thật — không có AI
def tinh_gia(dich_vu: str, do_phuc_tap: str) -> str:
    bang_gia = {
        "web":  {"don_gian": 5, "trung_binh": 10, "phuc_tap": 15},
        "logo": {"don_gian": 2, "trung_binh": 3,  "phuc_tap": 5}
    }
    gia = bang_gia[dich_vu][do_phuc_tap]
    return f"{gia} triệu đồng"

# Bước 3: Gửi câu hỏi + tools lên Claude
user_message = "Tôi muốn làm logo đơn giản giá bao nhiêu"
print(f"User: {user_message}\n")

response = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=256,
    tools=tools,
    system="Bạn là trợ lý của Leo Studio.",
    messages=[{"role": "user", "content": user_message}]
)

print(f"Stop reason: {response.stop_reason}")

# Bước 4: Kiểm tra Claude có muốn gọi tool không
if response.stop_reason == "tool_use":
    tool_call = next(b for b in response.content if b.type == "tool_use")
    print(f"Claude muốn gọi: {tool_call.name}({tool_call.input})")

    # Bước 5: Code của anh chạy tool thật
    ket_qua = tinh_gia(**tool_call.input)
    print(f"Kết quả tool: {ket_qua}\n")

    # Bước 6: Gửi kết quả lại cho Claude
    final = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=256,
        tools=tools,
        system="Bạn là trợ lý của Leo Studio.",
        messages=[
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": response.content},
            {"role": "user", "content": [{
                "type": "tool_result",
                "tool_use_id": tool_call.id,
                "content": ket_qua
            }]}
        ]
    )
    print(f"Claude: {final.content[0].text}")

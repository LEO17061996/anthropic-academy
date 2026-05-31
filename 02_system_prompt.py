import anthropic, sys
sys.stdout.reconfigure(encoding="utf-8")

client = anthropic.Anthropic()

# System prompt = "vai diễn" của Claude
# User message = câu hỏi của người dùng
response = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=256,
    system="Bạn là trợ lý của Leo Studio, chuyên tư vấn thiết kế web. Không trả lời về bất động sản.",
    messages=[
        {"role": "user", "content": "Giá căn hộ quận 7 hiện nay khoảng bao nhiêu?"}
    ]
)

print(response.content[0].text)
print("\n--- Usage ---")
print(f"Input tokens : {response.usage.input_tokens}")
print(f"Output tokens: {response.usage.output_tokens}")

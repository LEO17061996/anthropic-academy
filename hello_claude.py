import anthropic, sys
sys.stdout.reconfigure(encoding="utf-8")

# Khởi tạo client — đọc ANTHROPIC_API_KEY từ env tự động
client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-haiku-4-5",  # dùng Haiku để tiết kiệm credit khi học
    max_tokens=256,
    messages=[
        {"role": "user", "content": "Say 'Setup complete! Ready to learn.' in Vietnamese."}
    ]
)

print(message.content[0].text)

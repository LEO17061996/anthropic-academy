import anthropic, sys
sys.stdout.reconfigure(encoding="utf-8")

client = anthropic.Anthropic()

print("Streaming response (chữ hiện ra từng chút như ChatGPT):\n")

# Dùng stream=True → chữ hiện ra ngay, không chờ xong mới in
with client.messages.stream(
    model="claude-haiku-4-5",
    max_tokens=200,
    messages=[{"role": "user", "content": "Giải thích prompt caching là gì trong 3 câu."}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

print("\n\n✅ Stream done")

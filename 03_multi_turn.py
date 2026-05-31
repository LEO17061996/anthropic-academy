import anthropic, sys
sys.stdout.reconfigure(encoding="utf-8")

client = anthropic.Anthropic()

# Multi-turn: lưu lịch sử chat trong list messages
# Claude KHÔNG tự nhớ — anh phải tự gửi lại history mỗi lần
conversation_history = []

def chat(user_message: str) -> str:
    conversation_history.append({
        "role": "user",
        "content": user_message
    })

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=512,
        system="Bạn là trợ lý học tập. Trả lời ngắn gọn bằng tiếng Việt.",
        messages=conversation_history
    )

    assistant_reply = response.content[0].text

    # Lưu reply của Claude vào history để lần sau gửi lại
    conversation_history.append({
        "role": "assistant",
        "content": assistant_reply
    })

    return assistant_reply


# Giả lập 3 lượt chat có context
print("Turn 1:", chat("Python là gì?"))
print("\nTurn 2:", chat("Nó khác JavaScript ở điểm nào?"))
print("\nTurn 3:", chat("Cái nào phù hợp hơn để học AI?"))

print(f"\nTotal messages in history: {len(conversation_history)}")

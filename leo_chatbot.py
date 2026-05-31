"""
Leo Studio AI Chatbot
Kết hợp: RAG + Tool Use + Prompt Caching + Multi-turn + Streaming
"""
import anthropic, sys
sys.stdout.reconfigure(encoding="utf-8")

client = anthropic.Anthropic()

# ── 1. TÀI LIỆU (RAG) ──────────────────────────────────────────────────────
DOCUMENTS = [
    {"id": 1, "content": "Thiết kế web tại Leo Studio: landing page 5 triệu, web 5-10 trang 10 triệu, web phức tạp có admin 15 triệu. Thời gian 5-14 ngày làm việc."},
    {"id": 2, "content": "Thiết kế logo tại Leo Studio: 2-5 triệu. Bao gồm 3 concept, 2 lần chỉnh sửa, bàn giao file AI/PNG/SVG. Thời gian 3-5 ngày."},
    {"id": 3, "content": "Quy trình Leo Studio: Bước 1 khảo sát yêu cầu (1 ngày). Bước 2 báo giá và ký hợp đồng. Bước 3 thiết kế phát triển (5-14 ngày). Bước 4 nghiệm thu bàn giao. Bảo hành 30 ngày."},
    {"id": 4, "content": "Thanh toán Leo Studio: chuyển khoản ngân hàng hoặc MoMo. Cọc 50% khi bắt đầu, 50% còn lại khi nghiệm thu. Không hoàn tiền sau khi bắt đầu thiết kế."},
    {"id": 5, "content": "Leo Studio không nhận: app mobile, game, phần mềm desktop. Chỉ chuyên web và branding (logo, nhận diện thương hiệu)."},
    {"id": 6, "content": "Leo Studio liên hệ: Zalo 0779854336. Portfolio: leo-studio.pages.dev. Email: lethanhthuan17061996@gmail.com"},
]

# ── 2. TOOLS (Tool Use) ─────────────────────────────────────────────────────
TOOLS = [{
    "name": "tinh_gia",
    "description": "Tính giá chính xác dịch vụ Leo Studio. Dùng khi khách hỏi giá cụ thể.",
    "input_schema": {
        "type": "object",
        "properties": {
            "dich_vu": {"type": "string", "description": "'web' hoặc 'logo'"},
            "do_phuc_tap": {"type": "string", "description": "'don_gian', 'trung_binh', hoặc 'phuc_tap'"}
        },
        "required": ["dich_vu", "do_phuc_tap"]
    }
}]

def tinh_gia(dich_vu: str, do_phuc_tap: str) -> str:
    bang_gia = {
        "web":  {"don_gian": 5, "trung_binh": 10, "phuc_tap": 15},
        "logo": {"don_gian": 2, "trung_binh": 3,  "phuc_tap": 5}
    }
    gia = bang_gia.get(dich_vu, {}).get(do_phuc_tap, 0)
    return f"{gia} triệu đồng"

# ── 3. SYSTEM PROMPT với Prompt Caching ─────────────────────────────────────
SYSTEM = [{
    "type": "text",
    "text": """Bạn là trợ lý tư vấn của Leo Studio — chuyên thiết kế web và logo tại TP.HCM.

Quy tắc:
- Chỉ trả lời dựa trên thông tin trong <context> hoặc kết quả tool.
- KHÔNG suy luận hay bịa thông tin.
- Nếu không có thông tin → nói: "Mình chưa có thông tin này, anh/chị liên hệ Zalo 0779854336 nhé."
- Dịch vụ ngoài lĩnh vực → từ chối lịch sự + gợi ý dịch vụ phù hợp.
- Tone thân thiện, xưng "mình", kết bằng câu hỏi mở để tư vấn thêm.""",
    "cache_control": {"type": "ephemeral"}
}]

# ── 4. RAG: tìm tài liệu liên quan ─────────────────────────────────────────
def retrieve(query: str, top_k: int = 2) -> list:
    query_words = set(query.lower().split())
    scores = [(len(query_words & set(doc["content"].lower().split())), doc) for doc in DOCUMENTS]
    scores.sort(key=lambda x: x[0], reverse=True)
    return [doc for score, doc in scores[:top_k] if score > 0]

# ── 5. CHAT với multi-turn history ──────────────────────────────────────────
def chat(user_input: str, history: list) -> list:
    # RAG: inject context vào message
    docs = retrieve(user_input)
    context = "\n".join([d["content"] for d in docs])
    user_content = f"<context>\n{context}\n</context>\n\n{user_input}" if context else user_input

    history.append({"role": "user", "content": user_content})

    # Giới hạn history 10 lượt để tránh quá nặng
    if len(history) > 20:
        history = history[-20:]

    # Gọi API lần 1
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=512,
        system=SYSTEM,
        tools=TOOLS,
        messages=history
    )

    # Xử lý Tool Use
    if response.stop_reason == "tool_use":
        tool_call = next(b for b in response.content if b.type == "tool_use")
        tool_result = tinh_gia(**tool_call.input)

        history.append({"role": "assistant", "content": response.content})
        history.append({"role": "user", "content": [{
            "type": "tool_result",
            "tool_use_id": tool_call.id,
            "content": tool_result
        }]})

        # Gọi API lần 2 với streaming
        print("\n\033[36mLeo Studio:\033[0m ", end="", flush=True)
        final_text = ""
        with client.messages.stream(
            model="claude-sonnet-4-5",
            max_tokens=512,
            system=SYSTEM,
            tools=TOOLS,
            messages=history
        ) as stream:
            for text in stream.text_stream:
                print(text, end="", flush=True)
                final_text += text
        print("\n")
        history.append({"role": "assistant", "content": final_text})

    else:
        # Không dùng tool — streaming trực tiếp
        history[-1] = {"role": "user", "content": user_content}

        print("\n\033[36mLeo Studio:\033[0m ", end="", flush=True)
        final_text = ""
        with client.messages.stream(
            model="claude-sonnet-4-5",
            max_tokens=512,
            system=SYSTEM,
            tools=TOOLS,
            messages=history
        ) as stream:
            for text in stream.text_stream:
                print(text, end="", flush=True)
                final_text += text
        print("\n")
        history.append({"role": "assistant", "content": final_text})

    return history

# ── 6. MAIN LOOP ─────────────────────────────────────────────────────────────
def main():
    print("\033[1m╔══════════════════════════════╗\033[0m")
    print("\033[1m║   Leo Studio AI Chatbot      ║\033[0m")
    print("\033[1m╚══════════════════════════════╝\033[0m")
    print("Gõ 'quit' để thoát\n")

    history = []
    while True:
        try:
            user_input = input("\033[33mBạn:\033[0m ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nTạm biệt!")
            break

        if not user_input:
            continue
        if user_input.lower() in ["quit", "exit", "thoát"]:
            print("Tạm biệt! 👋")
            break

        history = chat(user_input, history)

if __name__ == "__main__":
    main()

import anthropic, sys
sys.stdout.reconfigure(encoding="utf-8")

client = anthropic.Anthropic()

# System prompt dài — giả lập tài liệu doanh nghiệp thật
LONG_SYSTEM = """Bạn là trợ lý của Leo Studio.

=== DỊCH VỤ ===
Thiết kế web: 5-15 triệu. Landing page: 5tr. Web 5-10 trang: 10tr. Web phức tạp: 15tr.
Thiết kế logo: 2-5 triệu. Bao gồm 3 concept, 2 lần sửa, file AI/PNG/SVG.
Marketing online: Google Ads, Facebook Ads, SEO. Báo giá theo dự án.

=== QUY TRÌNH ===
Bước 1: Khảo sát yêu cầu (1 ngày).
Bước 2: Báo giá và ký hợp đồng.
Bước 3: Thiết kế và phát triển (5-14 ngày).
Bước 4: Nghiệm thu và bàn giao. Bảo hành 30 ngày.

=== THANH TOÁN ===
Chuyển khoản ngân hàng hoặc MoMo. Cọc 50% khi bắt đầu, 50% khi nghiệm thu.

=== QUY TẮC TRẢ LỜI ===
Thân thiện, ngắn gọn, xưng mình. Không làm app mobile, game, phần mềm desktop.
Câu hỏi ngoài lĩnh vực → từ chối lịch sự và gợi ý dịch vụ phù hợp.
""" * 5  # Nhân 5 lần để system prompt đủ dài (>1024 tokens mới cache được)

def chat_with_cache(question: str):
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=200,
        # Dùng list thay vì string — để thêm cache_control
        system=[{
            "type": "text",
            "text": LONG_SYSTEM,
            "cache_control": {"type": "ephemeral"}  # ← bật cache
        }],
        messages=[{"role": "user", "content": question}]
    )

    usage = response.usage
    print(f"  Input tokens    : {usage.input_tokens}")
    print(f"  Cache write     : {getattr(usage, 'cache_creation_input_tokens', 0)}")
    print(f"  Cache read      : {getattr(usage, 'cache_read_input_tokens', 0)}")
    print(f"  Output tokens   : {usage.output_tokens}")
    print(f"  Reply: {response.content[0].text[:120]}...")
    print()

print("=== Request 1 (tạo cache lần đầu) ===")
chat_with_cache("Giá web bao nhiêu?")

print("=== Request 2 (đọc từ cache) ===")
chat_with_cache("Làm logo mất bao lâu?")

print("=== Request 3 (đọc từ cache) ===")
chat_with_cache("Thanh toán thế nào?")

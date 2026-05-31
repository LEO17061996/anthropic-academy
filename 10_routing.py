"""
Module 9: Routing Pattern
Router phân loại câu hỏi → xử lý đúng chỗ
"""
import anthropic, sys
sys.stdout.reconfigure(encoding="utf-8")

client = anthropic.Anthropic()

# ── ROUTER: phân loại câu hỏi (dùng Haiku — rẻ, nhanh) ─────────────────────
def classify(question: str) -> str:
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=10,
        temperature=0,
        messages=[{
            "role": "user",
            "content": f"""Phân loại câu hỏi sau vào 1 trong 4 loại:
GIA_CA: hỏi về giá, chi phí, báo giá
QUY_TRINH: hỏi về thời gian, quy trình, thanh toán  
NGOAI_LINH_VUC: hỏi dịch vụ Leo Studio không làm (app, game, phần mềm)
KHIEU_NAI: phàn nàn, không hài lòng, báo lỗi, yêu cầu hỗ trợ

Câu hỏi: {question}
Chỉ trả lời đúng 1 từ."""
        }]
    )
    label = response.content[0].text.strip().upper()
    # Normalize nếu Claude trả lời có khoảng trắng hay ký tự lạ
    for valid in ["GIA_CA", "QUY_TRINH", "NGOAI_LINH_VUC", "KHIEU_NAI"]:
        if valid in label:
            return valid
    return "QUY_TRINH"  # default

# ── HANDLERS: mỗi loại 1 system prompt chuyên biệt ──────────────────────────
HANDLERS = {
    "GIA_CA": {
        "system": "Bạn là chuyên gia tư vấn giá của Leo Studio. "
                  "Bảng giá: web landing 5tr, web 5-10 trang 10tr, web phức tạp 15tr, logo 2-5tr. "
                  "Tư vấn gói phù hợp dựa trên nhu cầu khách. Ngắn gọn, thân thiện, xưng mình.",
    },
    "QUY_TRINH": {
        "system": "Bạn là chuyên gia quy trình của Leo Studio. "
                  "Quy trình: khảo sát 1 ngày → ký HĐ → thiết kế 5-14 ngày → nghiệm thu. "
                  "Thanh toán: cọc 50%, còn 50% khi nghiệm thu. Bảo hành 30 ngày. "
                  "Giải thích rõ ràng, tạo cảm giác chuyên nghiệp.",
    },
    "NGOAI_LINH_VUC": {
        "system": "Bạn là trợ lý của Leo Studio. "
                  "Leo Studio chỉ làm web và logo. KHÔNG làm app, game, phần mềm. "
                  "Từ chối lịch sự, gợi ý dịch vụ web/logo nếu có liên quan. "
                  "Luôn kết bằng lời mời tư vấn thêm.",
    },
    "KHIEU_NAI": {
        "system": "Bạn là bộ phận chăm sóc khách hàng của Leo Studio. "
                  "Thể hiện sự đồng cảm, xin lỗi nếu cần. "
                  "Luôn đề xuất: liên hệ trực tiếp Zalo 0779854336 để giải quyết nhanh nhất. "
                  "Tone chân thành, không defensive.",
    },
}

def handle(question: str, route: str) -> str:
    handler = HANDLERS[route]
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=300,
        system=handler["system"],
        messages=[{"role": "user", "content": question}]
    )
    return response.content[0].text

# ── MAIN ─────────────────────────────────────────────────────────────────────
QUESTIONS = [
    "Web bán hàng cho shop thời trang giá bao nhiêu?",
    "Sau khi ký hợp đồng thì bao lâu có web?",
    "Leo Studio có làm app đặt đồ ăn không?",
    "Web mình làm xong nhưng load chậm quá, không hài lòng.",
]

print("=" * 55)
for q in QUESTIONS:
    route = classify(q)
    answer = handle(q, route)
    print(f"\n❓ {q}")
    print(f"🔀 Route: {route}")
    print(f"💬 {answer[:200]}...")
    print("-" * 55)

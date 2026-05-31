import anthropic, sys
sys.stdout.reconfigure(encoding="utf-8")

client = anthropic.Anthropic()

# --- Giả lập "tài liệu" của Leo Studio ---
# Thực tế: đây là file PDF, Word, hoặc DB của client
DOCUMENTS = [
    {
        "id": 1,
        "content": "Thiết kế web tại Leo Studio có giá từ 5-15 triệu đồng. "
                   "Web đơn giản (landing page): 5 triệu. "
                   "Web trung bình (5-10 trang): 10 triệu. "
                   "Web phức tạp (có admin, tích hợp): 15 triệu."
    },
    {
        "id": 2,
        "content": "Thiết kế logo tại Leo Studio từ 2-5 triệu đồng. "
                   "Bao gồm 3 concept, 2 lần chỉnh sửa, bàn giao file AI/PNG/SVG. "
                   "Thời gian: 3-5 ngày làm việc."
    },
    {
        "id": 3,
        "content": "Quy trình làm việc của Leo Studio: "
                   "Bước 1 - Khảo sát yêu cầu (1 ngày). "
                   "Bước 2 - Báo giá và ký hợp đồng. "
                   "Bước 3 - Thiết kế và phát triển (5-14 ngày). "
                   "Bước 4 - Nghiệm thu và bàn giao. "
                   "Bảo hành 30 ngày sau bàn giao."
    },
    {
        "id": 4,
        "content": "Leo Studio chấp nhận thanh toán: chuyển khoản ngân hàng, MoMo. "
                   "Cọc 50% khi bắt đầu, 50% còn lại khi nghiệm thu. "
                   "Không hoàn tiền sau khi bắt đầu thiết kế."
    },
    {
        "id": 5,
        "content": "Leo Studio không làm: app mobile, game, phần mềm desktop. "
                   "Chỉ chuyên web và branding (logo, nhận diện thương hiệu)."
    },
]

def retrieve(query: str, top_k: int = 2) -> list:
    """
    Tìm đoạn tài liệu liên quan nhất với câu hỏi.
    Đây là text search đơn giản — thực tế dùng vector search.
    """
    query_words = set(query.lower().split())
    scores = []

    for doc in DOCUMENTS:
        doc_words = set(doc["content"].lower().split())
        # Đếm số từ trùng nhau
        overlap = len(query_words & doc_words)
        scores.append((overlap, doc))

    # Sắp xếp theo điểm, lấy top_k cao nhất
    scores.sort(key=lambda x: x[0], reverse=True)
    return [doc for score, doc in scores[:top_k] if score > 0]

def rag_chat(question: str) -> str:
    # Bước 1: Tìm tài liệu liên quan
    relevant_docs = retrieve(question)

    if not relevant_docs:
        context = "Không có thông tin liên quan trong tài liệu."
    else:
        context = "\n\n".join([doc["content"] for doc in relevant_docs])

    print(f"[RAG tìm được {len(relevant_docs)} đoạn liên quan]")

    # Bước 2: Nhét context vào prompt, gửi Claude
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=256,
        system="Bạn là trợ lý của Leo Studio. "
       "Chỉ dùng thông tin trong <context> để trả lời. "
       "KHÔNG suy luận thêm. "
       "Khi khách hỏi dịch vụ ngoài khả năng → từ chối lịch sự "
       "+ gợi ý dịch vụ Leo Studio phù hợp nhất với nhu cầu khách. "
       "Tone thân thiện, xưng 'mình', kết bằng câu mời tư vấn thêm.",
        messages=[{
            "role": "user",
            "content": f"<context>\n{context}\n</context>\n\nCâu hỏi: {question}"
        }]
    )
    return response.content[0].text

# Test với 3 câu hỏi
questions = [
    "Thanh toán bằng tiền mặt được không?",
    "Làm logo mất bao lâu?",
    "Leo Studio có làm app không?",
]

for q in questions:
    print(f"\nUser: {q}")
    print(f"Claude: {rag_chat(q)}")
    print("-" * 40)

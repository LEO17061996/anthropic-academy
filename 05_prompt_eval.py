import anthropic, sys
sys.stdout.reconfigure(encoding="utf-8")

client = anthropic.Anthropic()

# --- System prompt cần test ---
SYSTEM_PROMPT = """Bạn là trợ lý tư vấn của Leo Studio.
Chuyên thiết kế web, logo, và marketing online.
Giá thiết kế web từ 5-15 triệu. Logo từ 2-5 triệu.
Luôn trả lời ngắn gọn, thân thiện, bằng tiếng Việt."""

# --- Bộ test cases ---
TEST_CASES = [
    {
        "question": "Giá thiết kế web bao nhiêu?",
        "must_contain": ["triệu"],          # code check: phải có chữ này
        "must_not_contain": ["dollar", "$"], # code check: không được có cái này
    },
    {
        "question": "Leo Studio có làm logo không?",
        "must_contain": ["logo"],
        "must_not_contain": [],
    },
    {
        "question": "Bạn có thể dạy tôi học lái xe không?",
        "must_contain": [],
        "must_not_contain": [ "có thể dạy"],  # phải từ chối
    },
]

def code_check(response: str, case: dict) -> tuple[bool, str]:
    """Cách 1: Code chấm — check keyword cứng"""
    for word in case["must_contain"]:
        if word.lower() not in response.lower():
            return False, f"Thiếu từ bắt buộc: '{word}'"
    for word in case["must_not_contain"]:
        if word.lower() in response.lower():
            return False, f"Có từ không được phép: '{word}'"
    return True, "OK"

def model_check(question: str, response: str,system_prompt: str) -> tuple[int, str]:
    """Cách 2: Claude chấm Claude — đánh giá chất lượng"""
    result = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=100,
        temperature=0,
        messages=[{
            "role": "user",
            "content": f"""Đây là system prompt của chatbot:
{system_prompt}

Câu hỏi user: {question}
Response của chatbot: {response}

Dựa vào system prompt trên, chấm điểm response từ 1-5:
5 = Đúng với system prompt, đầy đủ, thân thiện
3 = Đúng nhưng thiếu sót
1 = Sai hoặc mâu thuẫn với system prompt

Chỉ trả lời: SCORE: [số] | LÝ DO: [1 câu]"""
        }]
    )
    text = result.content[0].text
    score = int(text.split("SCORE:")[1].split("|")[0].strip())
    reason = text.split("LÝ DO:")[1].strip()
    return score, reason

# --- Chạy eval ---
print("=" * 50)
print("PROMPT EVALUATION REPORT")
print("=" * 50)

passed = 0
for i, case in enumerate(TEST_CASES):
    print(f"\nTest {i+1}: '{case['question']}'")

    # Lấy response từ Claude
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=200,
        system=SYSTEM_PROMPT,
        temperature=0,
        messages=[{"role": "user", "content": case["question"]}]
    ).content[0].text

    print(f"Response: {response[:100]}...")

    # Chấm bằng code
    code_ok, code_msg = code_check(response, case)
    print(f"Code check : {'✅' if code_ok else '❌'} {code_msg}")

    # Chấm bằng model
    score, reason = model_check(case["question"], response, SYSTEM_PROMPT)
    print(f"Model check: {'✅' if score >= 3 else '⚠️'} Score {score}/5 — {reason}")

    if code_ok and score >= 3:
        passed += 1

print(f"\n{'='*50}")
print(f"KẾT QUẢ: {passed}/{len(TEST_CASES)} tests passed")
print("=" * 50)

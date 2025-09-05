# --- GPT 프롬프트 ---

# 채팅 의도 분류 프롬프트
def classify_intent_prompt(user_message: str) -> list[dict]:
    return [
        {"role": "system", "content": "당신은 사용자 질문의 의도를 [제품 추천] 또는 [단순 대화] 중 하나로만 분류하는 AI입니다."},
        {"role": "user", "content": user_message}
    ]

# 프리셋 임시 제목 생성 프롬프트
def generate_preset_title_prompt(chat_history_str: str) -> list[dict]:
    prompt = f"다음 대화 내용의 핵심 주제를 10자 이내의 제목으로 요약해줘.\n\n{chat_history_str}"
    return [{"role": "user", "content": prompt}]

# 예상 질문 생성 프롬프트
def generate_quick_replies_prompt(user_info_str: str) -> list[dict]:
    prompt = f"""
{user_info_str}

위 사용자 데이터를 가진 사람이 AI 뷰티 어드바이저에게 할 법한 질문 4개를 생성해줘. 각 질문은 다음 조건을 반드시 지켜야 해:
1. 제공된 사용자 안면부 피부 분석 데이터와 시용자의 바우만 피부 타입 테스트 설문조사 결과 데이터를 기반으로 질문을 만들어줘. 
2. 여드름 피부 문제에 대한 질문을 필수적으로 2개 생성해줘.
3. 한국어로 작성해줘.
4. 각 질문을 줄바꿈으로만 구분하고, 번호나 다른 기호는 절대 붙이지 마.
"""
    return [
        {"role": "system", "content": "당신은 사용자의 복합적인 피부 데이터를 분석하여, 가장 적절하고 개인화된 스킨케어 질문을 생성하는 AI입니다."},
        {"role": "user", "content": prompt}
    ]

# 제품 사용 설명 프롬프트
def generate_usage_guide_prompt(product_name: str) -> list[dict]:
    prompt = f"""
'{product_name}' 제품의 상세한 사용 방법과 주요 성분, 주의사항을 알려줘.

[지시사항]
1. 제품을 추천할 때는 어떤 성분 때문에, 왜 사용자에게 좋은지 그 이유를 반드시 설명해야 합니다.
2. 추천한 제품을 어떤 순서로, 어떻게 사용하면 좋을지 '스킨케어 루틴'을 상세히 제안해주세요. (예: 아침/저녁, 사용 순서, 주의사항 등)
3. 전문가적이고 신뢰도 높은 말투를 사용하되, 너무 딱딱하지 않게 친근한 어조를 유지해주세요.
"""
    return [{"role": "user", "content": prompt}]

# 제품 추천 프롬프트
def get_recommendation_prompt(user_info_str: str, chat_history_str: str, products_str: str, query: str) -> list[dict]:
    user_prompt = f"""
[이전 대화 내용]
{chat_history_str}

[사용자 정보 요약]
{user_info_str}

[사용자의 현재 질문]
{query}

[시스템이 찾아낸 관련 제품 목록]
{products_str}

[지시사항]
1. 위의 모든 정보를 종합하여, 사용자에게 찾아낸 3가지 제품을 추천하는 '소개글'을 70자 이내로 작성해주세요.
2. 소개글 마지막에는 "제품 사용법이 궁금하시면 아래 버튼을 클릭해주시고, 다른 문의는 채팅으로 입력해주세요." 라는 안내 문구를 반드시 포함해주세요.
3. 소개글 작성 후, 빈 줄 하나를 띄고(예: \\n\\n), 각 제품에 대한 '간단한 설명'을 15자 이내로 각각 한 줄씩, 총 3줄을 생성해주세요. (제품명은 절대 포함하지 마세요)

[출력 예시]
고객님의 민감한 피부와 보습 고민에 맞춰 다음 제품들을 추천해 드립니다. 제품 사용법이 궁금하시면 아래 버튼을 클릭해주시고, 다른 문의는 채팅으로 입력해주세요.

피부 장벽 강화에 도움
수분 집중 공급 케어
저자극 진정 효과
"""
    return [
        {"role": "system", "content": "당신은 대한민국 최고의 피부 관리 전문가입니다. 사용자의 정보를 바탕으로 제품을 소개하고, 지정된 형식에 맞춰 버튼 텍스트를 생성해야 합니다."},
        {"role": "user", "content": user_prompt}
    ]
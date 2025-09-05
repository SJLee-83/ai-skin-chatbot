# --- OpenAI 활용 서비스 ---

from app.core import prompts
from openai import AzureOpenAI
import logging

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self, client: AzureOpenAI, embedding_model: str, chat_model: str):
        self.client = client
        self.embedding_model = embedding_model
        self.chat_model = chat_model
        logger.info("OpenAIService initialized")

    # 채팅 의도 분류
    def classify_intent(self, user_message: str) -> str:
        logger.info("Classifying intent...")
        try:
            messages = prompts.classify_intent_prompt(user_message)
            # 헬퍼 함수 호출
            intent_raw = self.get_chat_completion(messages, max_tokens=20, temperature=0)
            intent = intent_raw.replace('[', '').replace(']', '')
            return intent if intent in ["제품 추천", "단순 대화"] else "제품 추천"
        except Exception as e:
            logger.warning(f"Intent classification failed: {e}. Defaulting to '제품 추천'.")
            return "제품 추천"

    # 프리셋 임시 제목 생성    
    def generate_preset_title(self, chat_history_str: str) -> str:
        logger.info("Generating preset title...")
        messages = prompts.generate_preset_title_prompt(chat_history_str)
        title_raw = self.get_chat_completion(messages, max_tokens=30)
        return title_raw.replace('"', '').replace("'", "")
    
    # 예상 질문 생성
    def generate_quick_replies(self, user_info_str: str) -> list[str]:
        logger.info("Generating quick replies...")
        messages = prompts.generate_quick_replies_prompt(user_info_str)
        content = self.get_chat_completion(messages, max_tokens=200)
        quick_replies = [line.strip() for line in content.strip().split("\n") if line.strip()]
        return quick_replies[:4]    
    
    # 제품 사용법 설명
    def generate_usage_guide(self, product_name: str) -> str:
        logger.info(f"Generating usage guide for: {product_name}")
        messages = prompts.generate_usage_guide_prompt(product_name)
        return self.get_chat_completion(messages)

    # 범용 Chat Completion 헬퍼 함수
    def get_chat_completion(self, messages: list[dict], max_tokens: int = None, temperature: float = 0.7) -> str:
        try:
            params = { "model": self.chat_model, "messages": messages, "temperature": temperature }
            if max_tokens is not None:
                params["max_tokens"] = max_tokens
            response = self.client.chat.completions.create(**params)
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Chat completion error: {e}", exc_info=True)
            raise e
        
    # 텍스트 임베딩
    def get_embedding(self, text: str) -> list[float]:
        logger.info("Getting embedding vector...")
        response = self.client.embeddings.create(input=text, model=self.embedding_model)
        return response.data[0].embedding
    
    # 제품 추천
    def get_recommendation_response(self, user_info_str: str, chat_history_str: str, products: list, query: str) -> tuple[str, list]:
        logger.info("Getting recommendation response...")
        products_str = "\n\n".join([f"- 제품명: {p['product_name']}\n  카테고리: {p['product_type']}\n  주요성분: {p['product_ingredients']}\n  제품소개문구: {p['product_description']}" for p in products])
        
        messages = prompts.get_recommendation_prompt(user_info_str, chat_history_str, products_str, query)
        full_response = self.get_chat_completion(messages)

        parts = full_response.split('\n\n', 1)
        ai_response = parts[0]
        descriptions_str = parts[1] if len(parts) > 1 else ""
        descriptions = [line.strip() for line in descriptions_str.split('\n') if line.strip()]

        if len(descriptions) != len(products):
            logger.warning(f"Description count mismatch from OpenAI. Products: {len(products)}, Descriptions: {len(descriptions)}. Using fallback.")
            descriptions = ["상세 정보 보기"] * len(products)

        button_texts = [f"{p['product_name']}: {desc}" for p, desc in zip(products, descriptions)]
        return ai_response, button_texts
    
    # 단순 상담
    def get_simple_chat_response(self, messages: list[dict]) -> str:
        logger.info("Getting simple chat response...")
        return self.get_chat_completion(messages)
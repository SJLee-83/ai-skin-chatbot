from app.repositories.chat_repository import ChatRepository
from app.caching.session_cache import SessionCache
from app.services.openai_service import OpenAIService
from datetime import date, datetime
import logging
import pytz

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, repository: ChatRepository, cache: SessionCache, openai_service: OpenAIService):
        self.repository = repository
        self.cache = cache
        self.openai_service = openai_service
        self.kst = pytz.timezone("Asia/Seoul")
        logger.info("ChatService initialized")

    # 채팅방 첫 입장 시 채팅 내역 or 예상 질문 호출
    def get_initial_messages(self, user_key: str) -> list:
        logger.info(f"Getting initial messages for user: {user_key}")
        session_data = self.cache.get_session_data(user_key)
        chat_history = session_data.get("chat_history", [])
        
        initial_messages = []
        if chat_history:
            for i, msg in enumerate(chat_history):
                message_item = {
                    "id": f"{msg.get('role', 'bot')}-{i}",
                    "type": "bot" if msg.get("role") == "assistant" else "user",
                    "text": msg.get("content", ""),
                    "time": msg.get("time", "")
                }
                if msg.get("quickReplies"):
                    message_item["quickReplies"] = msg.get("quickReplies")
                initial_messages.append(message_item)
        else:
            user_info = self.repository.get_user_and_skin_data(user_key)
            user_info_str = self._get_processed_user_data_as_string(user_info)
            quick_replies = self.openai_service.generate_quick_replies(user_info_str)
            welcome_message = {
                "id": "bot-welcome",
                "type": "bot",
                "text": "무엇을 도와드릴까요?",
                "time": datetime.now(self.kst).strftime("%p %I:%M").replace("AM", "오전").replace("PM", "오후"),
                "quickReplies": quick_replies
            }
            initial_messages.append(welcome_message)
            self.cache.save_session_data(user_key, {"state": "initial_message", "chat_history": [], "context": {}})

        return initial_messages

    # 메인 라우터
    def process_chat_request(self, user_key: str, received_text: str) -> dict:
        logger.info(f"----- New Request Start ----- User Key: {user_key}, Received Text: '{received_text}'")

        session_data = self.cache.get_session_data(user_key)
        current_state = session_data.get("state", "initial_message")
        logger.info(f"Current State from Cache: {current_state}")

        context = session_data.get("context", {})
        recommended_products = context.get("recommended_products", [])
        selected_product = next((p for p in recommended_products if p.get("button_text") == received_text), None)

        if current_state == "initial_message" and selected_product:
            logger.info("Product button click detected. Changing state to 'product_recommendation'.")
            current_state = "product_recommendation"
            session_data["context"]["selected_product"] = selected_product
        
        handler_map = {
            "initial_message": self._handle_initial_message,
            "product_recommendation": self._handle_product_recommendation,
            "product_usage": self._handle_product_usage
        }
        handler = handler_map.get(current_state, self._handle_initial_message)
        logger.info(f"Calling Handler: {handler.__name__}")

        response_data, new_session_data = handler(user_key, received_text, session_data)

        self.cache.save_session_data(user_key, new_session_data)
        logger.info("----- Request End -----")
        return response_data
    
    # 채팅 기록 초기화 로직
    def reset_chat(self, user_key: str) -> dict:
        logger.info(f"Resetting chat for user: {user_key}")
        self.cache.reset_session(user_key)
        
        user_info = self.repository.get_user_and_skin_data(user_key)
        user_info_str = self._get_processed_user_data_as_string(user_info)
        new_quick_replies = self.openai_service.generate_quick_replies(user_info_str)
        
        return {"quick_replies": new_quick_replies}
    
    # 상태별 handler
    # state = initial_message
    def _handle_initial_message(self, user_key: str, received_text: str, session_data: dict) -> tuple[dict, dict]:
        logger.info("Executing `_handle_initial_message`...")
        chat_history = session_data.get("chat_history", [])
        now_time_str = datetime.now(self.kst).strftime("%p %I:%M").replace("AM", "오전").replace("PM", "오후")
        
        # --- 의도 분류 ---
        intent = self.openai_service.classify_intent(received_text)
        logger.info(f"Intent classified as: {intent}")

        if intent == "단순 대화":
            messages = ([{"role": "system", "content": "당신은 친절한 AI 챗봇입니다."}] + chat_history + [{"role": "user", "content": received_text}])
            ai_response = self.openai_service.get_simple_chat_response(messages)
            
            chat_history.append({"role": "user", "content": received_text, "time": now_time_str})
            chat_history.append({"role": "assistant", "content": ai_response, "time": now_time_str})
            session_data.update({"state": "initial_message", "chat_history": chat_history, "context": {}})
            
            return {"reply": ai_response}, session_data
        
        else: # 제품 추천
            chat_history.append({"role": "user", "content": received_text, "time": now_time_str})
            
            user_info = self.repository.get_user_and_skin_data(user_key)
            user_info_str = self._get_processed_user_data_as_string(user_info)
            skin_type_details = self.repository.get_skin_type_details(user_info.get("survey_data", {}).get("baumann_skin_type"))
            
            embedding_input = f"{user_info_str}\n\n[피부타입 상세정보]\n{skin_type_details}\n\n[사용자 질문]\n{received_text}"
            embedding_vector = self.openai_service.get_embedding(embedding_input)
            retrieved_products = self.repository.search_products_by_embedding(embedding_vector, limit=3)
            
            chat_history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])
            ai_response, button_texts = self.openai_service.get_recommendation_response(user_info_str, chat_history_str, retrieved_products, received_text)
            
            chat_history.append({"role": "assistant", "content": ai_response, "time": now_time_str, "quickReplies": button_texts})
            
            new_context = {"recommended_products": retrieved_products}
            session_data.update({"state": "initial_message", "chat_history": chat_history, "context": new_context})
            
            return {"reply": ai_response, "quick_replies": button_texts}, session_data

    # state = product_recommendation
    def _handle_product_recommendation(self, user_key: str, received_text: str, session_data: dict) -> tuple[dict, dict]:
        logger.info("Executing `_handle_product_recommendation`...")
        chat_history = session_data.get("chat_history", [])
        context = session_data.get("context", {})
        now_time_str = datetime.now(self.kst).strftime("%p %I:%M").replace("AM", "오전").replace("PM", "오후")
        chat_history.append({"role": "user", "content": received_text, "time": now_time_str})

        selected_product = context["selected_product"]
        usage_guide = self.openai_service.generate_usage_guide(selected_product['product_name'])
        context["selected_product"]["usage_guide"] = usage_guide

        ai_response = f"{usage_guide}\n\n이 제품 정보를 프리셋에 저장하시겠습니까?"
        quick_replies = ["예", "아니요"]
        
        chat_history.append({"role": "assistant", "content": ai_response, "time": now_time_str, "quickReplies": quick_replies})
        
        session_data.update({"state": "product_usage", "chat_history": chat_history, "context": context})
        return {"reply": ai_response, "quick_replies": quick_replies}, session_data
    
    # state = product_usage
    def _handle_product_usage(self, user_key: str, received_text: str, session_data: dict) -> tuple[dict, dict]:
        logger.info("Executing `_handle_product_usage`...")
        chat_history = session_data.get("chat_history", [])
        context = session_data.get("context", {})
        now_time_str = datetime.now(self.kst).strftime("%p %I:%M").replace("AM", "오전").replace("PM", "오후")
        chat_history.append({"role": "user", "content": received_text, "time": now_time_str})
        
        if "예" in received_text:
            logger.info("User chose to save to preset.")
            try:
                chat_history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])
                preset_title = self.openai_service.generate_preset_title(chat_history_str)
                self.repository.save_preset(user_key, preset_title, context["selected_product"])
                ai_response = "프리셋에 성공적으로 저장되었습니다.\n\n다른 궁금한 점이 있다면 편하게 질문해주세요."
            except Exception as e:
                ai_response = f"프리셋 저장 중 오류가 발생했습니다: {e}"
        else: # "아니요"
            logger.info("User chose not to save to preset.")
            ai_response = "알겠습니다. 다른 궁금한 점이 있다면 편하게 질문해주세요."

        chat_history.append({"role": "assistant", "content": ai_response, "time": now_time_str})
        session_data.update({"state": "initial_message", "chat_history": chat_history, "context": {}})
        return {"reply": ai_response}, session_data

    # 사용자 데이터 string 형식으로 변환
    def _get_processed_user_data_as_string(self, user_info: dict) -> str:
        logger.info("Processing user data into string format...")
        
        survey_scores = user_info.get("survey_data", {})
        
        do_score = survey_scores.get("baumann_do_score", 0)
        if 33 <= do_score <= 44: do_desc = "매우 유분이 많은 피부 (악지성)"
        elif 27 <= do_score < 33: do_desc = "약간 유분이 많은 피부 (약간 지성)"
        elif 17 <= do_score < 27: do_desc = "약간 건조한 피부 (약간 건성)"
        else: do_desc = "매우 건조한 피부 (건성)"
        
        sr_score = survey_scores.get("baumann_sr_score", 0)
        if 34 <= sr_score <= 72: sr_desc = "매우 민감한 피부"
        elif 30 <= sr_score < 34: sr_desc = "약간 민감한 피부"
        elif 25 <= sr_score < 30: sr_desc = "약간 저항성이 있는 피부"
        else: sr_desc = "저항성이 강한 피부"

        pn_score = survey_scores.get("baumann_pn_score", 0)
        pn_desc = "과색소침착피부" if 31 <= pn_score <= 45 else "비과색소침착피부"

        wt_score = survey_scores.get("baumann_wt_score", 0)
        wt_desc = "주름에 취약한 피부" if 41 <= wt_score <= 85 else "탄력 있는 피부"

        birth_str = user_info.get("user_profile", {}).get("birth")
        age = "알 수 없음"
        if birth_str:
            today = date.today()
            birth_date = date.fromisoformat(birth_str)
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

        user_profile = user_info.get('user_profile', {})
        skin_analysis = user_info.get('skin_analysis', {})
        survey_data = user_info.get('survey_data', {})

        return f"""
[사용자 기본 정보]
- 나이: {age}세
- 성별: {user_profile.get('gender', '알 수 없음')}

[사용자 피부 분석 데이터]
- 안면부 여드름 개수: {skin_analysis.get('acne_count', 0)}개
- 안면부 여드름 면적 비율: {skin_analysis.get('acne_area_ratio', 0.0)}%
- 안면부 홍조 면적 비율: {skin_analysis.get('redness_area_ratio', 0.0)}%

[사용자 설문 조사 데이터 (바우만 피부 타입 테스트)]
- D/O 타입: {do_desc}
- S/R 타입: {sr_desc}
- P/N 타입: {pn_desc}
- W/T 타입: {wt_desc}
- 최종 피부 타입: {survey_data.get('baumann_skin_type', '알 수 없음')}
"""    
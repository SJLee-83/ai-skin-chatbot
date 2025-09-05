from app.services.chat_service import ChatService
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

# --- Pydantic 요청 모델 정의 ---
class UserKeyRequest(BaseModel):
    user_key: str

class ChatRequest(BaseModel):
    user_key: str
    message: str

class ResetRequest(BaseModel):
    user_key: str

# --- APIRouter 생성 ---
router = APIRouter()

# --- API 엔드포인트들 ---
# 채팅방 첫 입장 시 호출되는 API 엔드포인트
@router.post("/start-chat")
async def start_chat(request: Request, user_key_request: UserKeyRequest):
    try:
        # 이제 request.app.state에서 chat_service를 가져옵니다.
        chat_service: ChatService = request.app.state.chat_service
        
        # 서비스 계층의 로직 호출 (이하 동일)
        initial_messages = chat_service.get_initial_messages(user_key_request.user_key)
        initial_data = {"initialMessages": initial_messages}
        return JSONResponse(content=initial_data)
        
    except Exception as e:
        # exc_info=True로 에러 상세 정보 자동 기록
        logger.error(f"❌ [Controller] /start-chat Error: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": "채팅방 입장에 실패했습니다."})

# 모든 메시지 처리를 담당하는 API 엔드포인트
@router.post("/message")
async def receive_message(request: Request, chat_request: ChatRequest):
    try:
        chat_service: ChatService = request.app.state.chat_service
        response_data = chat_service.process_chat_request(user_key=chat_request.user_key, received_text=chat_request.message)
        return JSONResponse(content=response_data)
    except Exception as e:
        logger.error(f"❌ [Controller] /message Error: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"reply": "서버 내부 오류가 발생했습니다."})

# 채팅 기록 초기화 API 엔드포인트
@router.post("/reset")
async def reset_chat(request: Request, reset_request: ResetRequest):
    try:
        chat_service: ChatService = request.app.state.chat_service
        response_data = chat_service.reset_chat(user_key=reset_request.user_key)
        return JSONResponse(content=response_data)
    except Exception as e:
        logger.error(f"❌ [Controller] /reset Error: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": "대화 기록 초기화에 실패했습니다."})

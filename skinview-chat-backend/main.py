import os
import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from openai import AzureOpenAI
import psycopg2
import redis

from app.api.home_controller import router as home_router
from app.repositories.chat_repository import ChatRepository
from app.caching.session_cache import SessionCache
from app.services.openai_service import OpenAIService
from app.services.chat_service import ChatService

# --- 로깅 기본 설정 ---
# 로그 메시지 형식: [시간] - [로거 이름] - [로그 레벨] - [메시지]
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# .env 파일 로드
load_dotenv()

# --- 설정 정보 로드 ---
AZURE_CONFIG = {
    "api_key": os.getenv("AZURE_API_KEY"),
    "azure_endpoint": os.getenv("AZURE_ENDPOINT"),
    "api_version": os.getenv("AZURE_API_VERSION")
}
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}
REDIS_CONFIG = {
    "host": os.getenv("REDIS_HOST"),
    "port": int(os.getenv("REDIS_PORT", 6379)), # 기본값을 설정하고 정수형으로 변환
    "db": int(os.getenv("REDIS_DB", 0))
}
EMBEDDING_MODEL_NAME = os.getenv("AZURE_EMBEDDING_MODEL_NAME")
DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")


# --- Lifespan: 애플리케이션 시작/종료 시 의존성 조립 ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버 시작 시 실행
    logger.info("🚀 [Lifespan] 서버 시작: 리소스를 초기화하고 서비스를 조립합니다.")
    
    # 1. 핵심 리소스 연결
    db_conn = psycopg2.connect(**DB_CONFIG)
    redis_conn = redis.Redis(**REDIS_CONFIG, decode_responses=True)
    openai_client = AzureOpenAI(**AZURE_CONFIG)
    
    # 2. 각 계층의 객체 생성
    chat_repo = ChatRepository(db_conn)
    session_cache = SessionCache(redis_conn)
    openai_service = OpenAIService(openai_client, EMBEDDING_MODEL_NAME, DEPLOYMENT_NAME)
    
    # 3. 서비스 계층에 의존성 주입하여 최종 서비스 객체 생성
    chat_service = ChatService(chat_repo, session_cache, openai_service)
    
    # 4. 앱 상태에 최종 서비스 객체 저장
    app.state.chat_service = chat_service
    
    logger.info("✅ [Lifespan] 모든 서비스가 성공적으로 조립되었습니다.")
    
    yield
    
    # === 서버 종료 시 실행 ===
    logger.info("🌙 [Lifespan] 서버 종료: 리소스를 정리합니다.")
    if db_conn:
        db_conn.close()
        logger.info("✔️ [Lifespan] DB 연결이 성공적으로 닫혔습니다.")

# --- FastAPI 앱 생성 및 라우터 연결 ---
app = FastAPI(lifespan=lifespan)
app.include_router(home_router, prefix="/api")

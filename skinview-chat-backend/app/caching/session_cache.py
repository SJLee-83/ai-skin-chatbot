# --- Redis(cache) ---

import json
import logging

logger = logging.getLogger(__name__)

class SessionCache:
    def __init__(self, redis_conn):
        self.redis_conn = redis_conn
        logger.info("SessionCache initialized")

    # 채팅 기록, context(사용자 정보, 선택 제품 정보 등) 호출
    def get_session_data(self, user_key: str) -> dict:
        logger.info(f"Getting session for user: {user_key}")
        session_json = self.redis_conn.get(user_key)
        if session_json:
            logger.info(f"Session found in cache for user: {user_key}")
            return json.loads(session_json)
        logger.info(f"No session in cache for user: {user_key}. Returning default.")
        return {"state": "initial_message", "chat_history": [], "context": {}}
    
    # 캐시 삭제
    def reset_session(self, user_key: str):
        logger.info(f"Deleting session for user: {user_key}")
        self.redis_conn.delete(user_key)
                
    # 채팅 기록, context(사용자 정보, 선택 제품 정보 등) 저장
    def save_session_data(self, user_key: str, session_data: dict):
        new_state = session_data.get('state')
        logger.info(f"Saving session for user: {user_key}. New state: {new_state}")
        self.redis_conn.set(user_key, json.dumps(session_data, ensure_ascii=False), ex=300)

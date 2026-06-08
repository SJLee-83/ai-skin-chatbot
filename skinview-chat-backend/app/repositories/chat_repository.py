# --- 데이터베이스 ---

from datetime import date
import logging
import psycopg2
import psycopg2.extras

logger = logging.getLogger(__name__)

class ChatRepository:
    def __init__(self, db_conn):
        self.db_conn = db_conn
        logger.info("ChatRepository initialized")

    # 특정 피부 타입의 모든 상세 정보를 DB에서 호출
    def get_skin_type_details(self, skin_type: str) -> str:
        if not skin_type:
            return ""
        logger.info(f"Getting skin type details for: {skin_type}")
        with self.db_conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            sql = "SELECT baumann_info_category, baumann_info_content FROM baumann_info_tbl WHERE baumann_info_skin_type = %s;"
            cur.execute(sql, (skin_type,))
            results = cur.fetchall()
            
            full_text = "\n".join([f"[{row['baumann_info_category']}]\n{row['baumann_info_content']}" for row in results])
            
            logger.info(f"Found and combined {len(results)} info chunks for {skin_type}.")
            return full_text
        
    # DB에서 필요 데이터 호출
    def get_user_and_skin_data(self, user_key: str) -> dict:
        logger.info(f"Getting user and skin data for user_key: {user_key}")
        user_info = {}
        with self.db_conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            # analysis_photo_tbl에서 가장 최신 기록을 가져오는 서브쿼리 포함
            sql = """
                SELECT
                    u.user_birth,
                    u.user_gender,
                    s.survey_skin_do,
                    s.survey_skin_sr,
                    s.survey_skin_pn,
                    s.survey_skin_wt,
                    s.survey_skin_type,
                    s.survey_skin_combination_type,
                    a.analysis_photo_acne_count,
                    a.analysis_photo_acne_area,
                    a.analysis_photo_redness_area
                FROM
                    user_tbl u
                LEFT JOIN
                    survey_tbl s ON u.user_key = s.survey_user_key
                LEFT JOIN
                    (SELECT * FROM analysis_photo_tbl 
                     WHERE analysis_photo_user_key = %s 
                     ORDER BY analysis_photo_date DESC 
                     LIMIT 1) a ON u.user_key = a.analysis_photo_user_key
                WHERE
                    u.user_key = %s;
            """
            cur.execute(sql, (user_key, user_key))
            result = cur.fetchone()

            if result:
                logger.info(f"User data found for user_key: {user_key}")
                user_info = {
                    "user_profile": {
                        "birth": result["user_birth"].strftime('%Y-%m-%d') if result["user_birth"] else None,
                        "gender": result["user_gender"]
                    },
                    "skin_analysis": {
                        "acne_count": result["analysis_photo_acne_count"],
                        "acne_area_ratio": float(result["analysis_photo_acne_area"]) if result["analysis_photo_acne_area"] is not None else 0.0,
                        "redness_area_ratio": float(result["analysis_photo_redness_area"]) if result["analysis_photo_redness_area"] is not None else 0.0
                    },
                    "survey_data": {
                        "baumann_do_score": int(result["survey_skin_do"]) if result["survey_skin_do"] is not None else 0,
                        "baumann_sr_score": int(result["survey_skin_sr"]) if result["survey_skin_sr"] is not None else 0,
                        "baumann_pn_score": int(result["survey_skin_pn"]) if result["survey_skin_pn"] is not None else 0,
                        "baumann_wt_score": int(result["survey_skin_wt"]) if result["survey_skin_wt"] is not None else 0,
                        "baumann_skin_type": result["survey_skin_type"],
                        "is_combination_skin": result["survey_skin_combination_type"]
                    }
                }
            else:
                logger.warning(f"User data not found for user_key: {user_key}")
                user_info = {
                    "user_profile": {}, "skin_analysis": {}, "survey_data": {}
                }
                
        return user_info
    
    # 프리셋 저장
    def save_preset(self, user_key: str, title: str, product: dict):
        logger.info(f"Saving preset for user: {user_key}")
        with self.db_conn.cursor() as cur:
            sql = """
                INSERT INTO preset_tbl (preset_user_key, preset_concerns, preset_product_name, preset_usage_guide, preset_date)
                VALUES (%s, %s, %s, %s, %s)
            """
            cur.execute(sql, (user_key, title, product['product_name'], product['usage_guide'], date.today()))
        self.db_conn.commit()
        logger.info(f"✅ Preset saved for {user_key}: {title}")
        
    # 코사인 거리 계산으로 맞춤 제품 검색
    def search_products_by_embedding(self, embedding_vector: list, limit: int) -> list[dict]:
        logger.info(f"Searching for {limit} products by embedding vector.")
        # embedding_vector(임베딩 API가 만든 float 리스트)는 사용자 입력이 아닌 내부 생성값이라
        # pgvector 리터럴로 직접 구성한다. limit은 파라미터 바인딩으로 전달.
        vector_literal = "ARRAY[{}]::vector".format(",".join(map(str, embedding_vector)))
        with self.db_conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            search_sql = f"""
            SELECT product_name, product_type, product_ingredients, product_description
            FROM products_tbl
            ORDER BY product_embedding <=> {vector_literal} LIMIT %s;
            """
            cur.execute(search_sql, (limit,))
            results = cur.fetchall()
            logger.info(f"Found {len(results)} similar products from DB.")
            return [dict(row) for row in results]
        
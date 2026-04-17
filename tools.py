import sqlite3
import chromadb

# ChromaDB 연결 (PersistentClient를 사용해야 database.py에서 만든 데이터를 가져옴)
client = chromadb.PersistentClient(path="./chroma_db")
product_collection = client.get_collection(name="products")

def get_order_status(order_id: str):
    """
    사용자의 주문 번호(예: ORD001)를 통해 현재 배송 상태를 조회합니다.
    """
    try:
        conn = sqlite3.connect("shop.db")
        cursor = conn.cursor()
        # 주문 테이블에서 상태(status)와 상품명(product_name)을 가져옴
        cursor.execute("SELECT product_name, status FROM orders WHERE order_id = ?", (order_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return f"주문하신 상품 [{result[0]}]의 현재 상태는 '{result[1]}'입니다."
        return "해당 주문 번호를 찾을 수 없습니다. 번호를 다시 확인해 주세요."
    except Exception as e:
        return f"주문 조회 중 오류가 발생했습니다: {str(e)}"

def search_and_recommend(user_query: str):
    """
    사용자의 취향이나 요구사항(예: 여름에 입기 좋은 것, 노트북 보호 등)에 맞는 상품을 
    벡터 데이터베이스에서 검색하여 추천합니다.
    """
    try:
        # 질문과 가장 유사한 상품 2개를 검색
        results = product_collection.query(
            query_texts=[user_query],
            n_results=2
        )
        
        if results['documents'] and len(results['documents'][0]) > 0:
            recommended_list = results['documents'][0]
            # 단순히 리스트를 합치지 말고, 각 상품 정보를 명확히 구분해서 전달
            return "검색된 상품 데이터:\n" + "\n".join([f"- {doc}" for doc in recommended_list])
        
        return "현재 조건에 맞는 상품이 없습니다. 다른 스타일은 어떠신가요?"
    except Exception as e:
        return f"상품 추천 중 오류가 발생했습니다: {str(e)}"

# Gemini 모델 설정 시 전달할 도구 리스트
tools_list = [get_order_status, search_and_recommend]
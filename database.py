import sqlite3
import chromadb
import pandas as pd
import os
from datetime import datetime

db_name = "shop.db"

def init_all_databases():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # 주문 테이블 (분석용)
    cursor.execute("""
        CREATE TABLE orders (
            order_id TEXT PRIMARY KEY, user_name TEXT, product_name TEXT, 
            status TEXT, price INTEGER, order_date TEXT
        )
    """)

    # AI 생성 상품 테이블 (네이버 일괄등록 표준 컬럼)
    cursor.execute("""
        CREATE TABLE ai_generated_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            상품상태 TEXT DEFAULT '신상품',
            카테고리명 TEXT,
            상품명 TEXT,
            판매가 INTEGER,
            재고수량 INTEGER DEFAULT 999,
            AS전화번호 TEXT DEFAULT '010-1234-5678',
            상세설명 TEXT,
            대표이미지파일명 TEXT,
            상품태그 TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 대화 로그 테이블
    # 유저 질문, AI 응답, 의도 분류, 보강된 질문, 에러 여부 등을 기록
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            user_question TEXT,
            ai_category TEXT,
            ai_response TEXT,
            refined_query TEXT,
            is_error INTEGER DEFAULT 0
        )
    """)

    # 테스트용 주문 데이터 삽입
    # 분석 시나리오: '린넨 셔츠'가 베스트셀러, 최근 며칠간 매출 발생
    sample_orders = [
        ("ORD-001", "김철수", "시원한 린넨 셔츠", "배송완료", 35000, "2026-04-10"),
        ("ORD-002", "이영희", "냉감 아이스 슬랙스", "배송중", 42000, "2026-04-12"),
        ("ORD-003", "박민준", "시원한 린넨 셔츠", "배송완료", 35000, "2026-04-15"),
        ("ORD-004", "최지우", "기본 오버핏 반팔", "결제완료", 19000, "2026-04-16"),
        ("ORD-005", "정다은", "시원한 린넨 셔츠", "배송중", 35000, "2026-04-17"),
        ("ORD-006", "강현우", "냉감 아이스 슬랙스", "배송완료", 42000, "2026-04-18"),
        ("ORD-007", "윤서연", "여름용 버킷햇", "결제완료", 25000, "2026-04-18"),
        ("ORD-008", "임세영", "시원한 린넨 셔츠", "배송준비", 35000, "2026-04-19"),
        ("ORD-009", "한승범", "기본 오버핏 반팔", "배송완료", 19000, "2026-04-19"),
        ("ORD-010", "송재희", "냉감 아이스 슬랙스", "취소", 42000, "2026-04-19"),
    ]

    cursor.executemany("""
        INSERT INTO orders (order_id, user_name, product_name, status, price, order_date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, sample_orders)

    print(f"✅ SQLite: {len(sample_orders)}개의 주문 데이터가 삽입되었습니다.")
    conn.commit()
    conn.close()

# 로그 저장 전용 함수
def save_chat_log(question, category, response, refined_query, is_error=0):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("""
        INSERT INTO chat_logs (timestamp, user_question, ai_category, ai_response, refined_query, is_error)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (timestamp, question, category, response, refined_query, is_error))
    conn.commit()
    conn.close()

def save_generated_product(data):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ai_generated_products (카테고리명, 상품명, 판매가, 상세설명, 상품태그, 대표이미지파일명)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (data['category'], data['seo_title'], data['price'], data['html_desc'], data['tags'], data['img_name']))
    conn.commit()
    conn.close()

def get_all_products_for_excel():
    conn = sqlite3.connect(db_name)
    query = "SELECT 상품상태, 카테고리명, 상품명, 판매가, 재고수량, AS전화번호, 상세설명, 대표이미지파일명, 상품태그 FROM ai_generated_products ORDER BY created_at DESC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def init_vector_db():
    client = chromadb.PersistentClient(path="./chroma_db")
    if "products" in [c.name for c in client.list_collections()]: client.delete_collection("products")
    collection = client.create_collection(name="products")
    
    # 학습용 샘플
    samples = [
        {"id":"p1", "name":"시원한 린넨 셔츠", "desc":"<h3>여름철 필수! 천연 린넨의 쾌적함</h3><p>피부에 닿는 순간 시원합니다.</p><ul><li>통기성 우수</li></ul>", "price":"35,000"},
        {"id":"p2", "name":"냉감 아이스 슬랙스", "desc":"<h3>체감 온도 -3도! 아이스 쿨링</h3><p>구김 걱정 없는 고탄성 원단입니다.</p><ul><li>흡습속건</li></ul>", "price":"42,000"}
    ]
    for p in samples:
        collection.add(ids=[p['id']], documents=[f"상품명: {p['name']}\n설명: {p['desc']}"], metadatas={"name":p['name']})

if __name__ == "__main__":
    init_all_databases()
    init_vector_db()
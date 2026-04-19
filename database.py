import sqlite3
import chromadb
import pandas as pd
import os

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
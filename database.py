import sqlite3
import chromadb

def init_order_db(): # SQL 주문 DB 설정
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            user_name TEXT,
            product_name TEXT,
            status TEXT,
            price INTEGER,      
            order_date TEXT     
        )
    """)
    orders = [
        # 4월 초순: 여름 준비 시작으로 의류 강세
        ('ORD001', '김철수', '시원한 린넨 셔츠', '배송 완료', 35000, '2026-04-01'),
        ('ORD002', '이영희', '고속 무선 충전기', '결제 완료', 25000, '2026-04-02'),
        ('ORD003', '박지민', '냉감 아이스 슬랙스', '배송 완료', 42000, '2026-04-03'),
        ('ORD004', '최유리', '시원한 린넨 셔츠', '배송 완료', 35000, '2026-04-04'),
        ('ORD005', '정다은', '대용량 보냉 텀블러', '배송 중', 22000, '2026-04-05'),
        
        # 4월 중순: 재택근무/사무용품 수요 발생
        ('ORD006', '강민호', '무소음 블루투스 마우스', '배송 완료', 25000, '2026-04-10'),
        ('ORD007', '조세희', '기계식 키보드 (갈축)', '결제 완료', 89000, '2026-04-11'),
        ('ORD008', '윤서준', '맥북 프로 가죽 파우치', '배송 중', 49000, '2026-04-12'),
        ('ORD009', '임지혜', '무소음 블루투스 마우스', '배송 완료', 25000, '2026-04-13'),
        
        # 4월 말: 더워지는 날씨로 냉감 소재 및 선풍기 급증
        ('ORD010', '한승우', '휴대용 미니 선풍기', '결제 완료', 15000, '2026-04-15'),
        ('ORD011', '오지윤', '냉감 아이스 슬랙스', '배송 중', 42000, '2026-04-15'),
        ('ORD012', '김현우', '시원한 린넨 셔츠', '결제 완료', 35000, '2026-04-16'),
        ('ORD013', '신예은', '휴대용 미니 선풍기', '결제 완료', 15000, '2026-04-17'),
        ('ORD014', '송태섭', '탄탄한 오버핏 티셔츠', '배송 중', 19800, '2026-04-17'),
        ('ORD015', '채치수', '냉감 아이스 슬랙스', '결제 완료', 42000, '2026-04-17')
    ]
    cursor.executemany("INSERT OR REPLACE INTO orders VALUES (?,?,?,?,?,?)", orders)
    conn.commit()
    conn.close()
    print("주문 SQL DB 생성 완료!")

def init_product_db(): # 벡터 상품 DB 설정
    client = chromadb.PersistentClient(path="./chroma_db")
    
    if "products" in [c.name for c in client.list_collections()]:
        client.delete_collection("products")
    
    collection = client.create_collection(name="products")

    products = [
        # --- 의류/패션 ---
        {"id": "p1", "name": "시원한 린넨 셔츠", "desc": "여름에도 땀 흡수가 잘 되는 가벼운 마 소재, 통기성 우수", "price": "35,000원"},
        {"id": "p2", "name": "냉감 아이스 슬랙스", "desc": "입는 순간 시원한 쿨링 원단, 신축성이 좋은 여름 바지", "price": "42,000원"},
        {"id": "p3", "name": "탄탄한 오버핏 티셔츠", "desc": "비침 없는 두꺼운 면 소재, 데일리로 입기 좋은 반팔", "price": "19,800원"},
        {"id": "p4", "name": "경량 덕다운 조끼", "desc": "겨울철 코트 안에 입기 좋은 가볍고 따뜻한 오리털 베스트", "price": "55,000원"},
        
        # --- 디지털/IT ---
        {"id": "p5", "name": "맥북 프로 가죽 파우치", "desc": "충격 흡수가 뛰어난 고급 소가죽 케이스, 노트북 보호용", "price": "49,000원"},
        {"id": "p6", "name": "무소음 블루투스 마우스", "desc": "사무실이나 독서실에서 쓰기 좋은 조용한 클릭감, 무선 연결", "price": "25,000원"},
        {"id": "p7", "name": "기계식 키보드 (갈축)", "desc": "타건감이 좋으면서 소음은 적은 업무용 기계식 키보드", "price": "89,000원"},
        
        # --- 생활/가전 ---
        {"id": "p8", "name": "대용량 보냉 텀블러", "desc": "하루 종일 얼음이 녹지 않는 강력한 보냉 성능, 스테인리스 900ml", "price": "22,000원"},
        {"id": "p9", "name": "휴대용 미니 선풍기", "desc": "작지만 강력한 바람, 여름 야외 활동 필수템, USB 충전", "price": "15,000원"},
        {"id": "p10", "name": "암막 수면 안대", "desc": "빛을 완벽 차단하여 숙면을 돕는 부드러운 실크 소재", "price": "12,000원"}
    ]

    for p in products:
        # 검색 품질을 위해 이름, 설명, 가격 정보를 하나의 텍스트로 합침
        doc_text = f"상품명: {p['name']} / 설명: {p['desc']} / 가격: {p['price']}"
        
        collection.add(
            ids=[p['id']],
            documents=[doc_text],
            metadatas=[{"name": p['name'], "price": p['price']}]
        )
    print("상품 벡터 DB 생성 완료!")

if __name__ == "__main__":
    init_order_db()
    init_product_db()
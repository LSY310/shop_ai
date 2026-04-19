import sqlite3
import chromadb
import pandas as pd
import datetime
from database import save_generated_product, get_all_products_for_excel

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
    
def analyze_sales_report():
    """쇼핑몰의 전체 매출 통계를 분석하여 총 매출액, 판매 건수, 인기 상품 정보를 반환합니다."""
    try:
        # DB 연결 및 데이터 로드
        conn = sqlite3.connect("shop.db")
        # SQL 데이터를 Pandas DataFrame으로 바로 변환
        df = pd.read_sql_query("SELECT * FROM orders", conn)
        conn.close()

        if df.empty:
            return "현재 분석할 주문 데이터가 없습니다."

        # 2. 데이터 가공 및 분석
        df['price'] = pd.to_numeric(df['price']) # 가격 숫자 변환
        total_revenue = df['price'].sum()        # 총 매출
        total_count = len(df)                    # 총 판매 건수
        
        # 상품별 판매량 집계 및 베스트셀러 추출
        best_seller_series = df.groupby('product_name').size().sort_values(ascending=False)
        best_seller_name = best_seller_series.index[0]
        best_seller_count = best_seller_series.values[0]

        # Gemini에게 전달할 리포트 구성 (이 데이터를 보고 Gemini가 해석함)
        report = {
            "total_revenue": f"{total_revenue:,}원",
            "total_orders": f"{total_count}건",
            "best_seller": f"{best_seller_name} ({best_seller_count}건 판매)",
            "raw_data_summary": df[['product_name', 'price', 'order_date']].to_dict(orient='records')
        }
        
        return str(report) # Gemini가 읽기 좋게 문자열로 반환

    except Exception as e:
        return f"매출 분석 중 오류가 발생했습니다: {str(e)}"

def generate_smartstore_content(product_name, keywords, category, price):
    """
    브랜드 톤앤매너가 적용된 네이버용 HTML 상세페이지와 SEO 정보를 생성합니다.
    """
    try:
        # 톤앤매너 추출을 위한 검색
        results = product_collection.query(query_texts=[keywords], n_results=1)
        ref_text = results['documents'][0][0] if results['documents'] else "깔끔하고 친절한 말투"

        # Gemini가 이 형식을 지키도록 프롬프트 전달
        prompt = f"""
        당신은 네이버 스마트스토어 전문 카피라이터입니다. 
        [샘플 말투]를 반영하여 신상품 콘텐츠를 작성하세요.

        [샘플 말투]
        {ref_text[:100]}

        [입력 정보]
        상품명: {product_name} / 특징: {keywords} / 카테고리: {category} / 가격: {price}

        [출력 요구사항]
        1. 상품명: (25자 이내 SEO 최적화)
        2. 상세설명: (<div>, <h3>, <p> 태그만 사용한 HTML. [이미지] 삽입 구간 포함)
        3. 태그: (10개, 쉼표 구분)
        
        결과물은 반드시 '상품명:', '상세설명:', '태그:'로 구분해서 출력하세요.
        """
        return prompt
    except Exception as e:
        return f"콘텐츠 생성 준비 중 오류: {str(e)}"

def save_to_db(seo_title, html_desc, tags, price, category, original_name):
    """AI가 만든 결과물을 DB에 최종 저장합니다."""
    try:
        data = {
            'seo_title': seo_title,
            'html_desc': html_desc,
            'tags': tags,
            'price': price,
            'category': category,
            'img_name': f"{original_name}.jpg" # 이미지 파일명 자동 생성
        }
        save_generated_product(data)
        return "✅ 성공적으로 DB에 저장되었습니다."
    except Exception as e:
        return f"저장 중 오류: {str(e)}"

def export_naver_excel():
    """DB의 상품 데이터를 엑셀로 추출합니다."""
    try:
        df = get_all_products_for_excel()
        if df.empty: return "추출할 데이터가 없습니다."
        filename = f"naver_upload_{datetime.datetime.now().strftime('%Y%m%d')}.xlsx"
        df.to_excel(filename, index=False)
        return f"✅ 엑셀 생성 완료: {filename}"
    except Exception as e:
        return f"엑셀 생성 중 오류: {str(e)}"

# 도구 리스트 업데이트
tools_list = [
    get_order_status, 
    search_and_recommend, 
    analyze_sales_report, 
    generate_smartstore_content, 
    save_to_db,  # 저장을 위한 도구 추가
    export_naver_excel
]
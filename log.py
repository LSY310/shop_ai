import sqlite3
import pandas as pd

# Pandas가 내용을 생략하지 않도록 강제 설정
pd.set_option('display.max_columns', None)    # 모든 컬럼 표시
pd.set_option('display.max_colwidth', None)   # 컬럼 안의 긴 텍스트 다 보여주기
pd.set_option('display.width', 1000)          # 한 줄의 너비를 넓게 설정

# DB 연결
conn = sqlite3.connect('shop.db')

#query = "SELECT * FROM chat_logs ORDER BY timestamp DESC LIMIT 10"
query = "SELECT * FROM ai_generated_products"
df = pd.read_sql_query(query, conn)

print("--- [최신 AI 매니저 대화 로그] ---")
print(df)
conn.close()
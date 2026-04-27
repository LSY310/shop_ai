# app.py 전체 수정
import streamlit as st
from chat import ask_llm
import pandas as pd
import sqlite3
import plotly.express as px
import threading
import time
import schedule
from database import init_all_databases, init_vector_db, task # database.py에서 가져옴

# 스케줄러를 백그라운드에서 실행하는 함수
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)

# 앱 시작 시 초기화 및 스케줄러 시작 (딱 한 번만 실행)
if "scheduler_started" not in st.session_state:
    schedule.every().day.at("23:59").do(task)
    
    # 별도 스레드로 스케줄러 시작
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()
    st.session_state.scheduler_started = True

st.set_page_config(page_title="쇼핑몰 에이전트 OS", layout="wide")

# 사이드바 메뉴
menu = st.sidebar.selectbox("메뉴 선택", ["💬 AI 매니저 채팅", "📊 운영 대시보드 (BI)"])

if menu == "💬 AI 매니저 채팅":
    st.title("🛍️ 쇼핑몰 AI 매니저")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("무엇을 도와드릴까요?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.status("에이전트가 업무 수행 중...", expanded=True) as status:
                try:
                    full_response = ask_llm(prompt)
                    status.update(label="업무 완료!", state="complete", expanded=False)
                except Exception as e:
                    status.update(label="오류 발생", state="error")
                    full_response = "잠시 후 다시 시도해주세요."
            
            st.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

elif menu == "📊 운영 대시보드 (BI)":
    st.title("📊 시스템 운영 및 매출 모니터링")
    
    conn = sqlite3.connect("shop.db")
    
    # 상단 지표
    col1, col2, col3 = st.columns(3)
    logs_df = pd.read_sql("SELECT * FROM chat_logs", conn)
    
    with col1:
        st.metric("누적 대화 수", len(logs_df))
    with col2:
        err_count = logs_df['is_error'].sum()
        st.metric("시스템 에러율", f"{(err_count/len(logs_df)*100):.1f}%" if len(logs_df)>0 else "0%")
    with col3:
        # daily_summary 테이블 사용
        summary_df = pd.read_sql("SELECT * FROM daily_summary", conn)
        total_rev = summary_df['total_sales'].sum() if not summary_df.empty else 0
        st.metric("ETL 집계 총 매출", f"{total_rev:,}원")

    # 그래프 시각화
    st.divider()
    if not logs_df.empty:
        fig = px.histogram(logs_df, x="ai_category", title="사용자 요청 의도 분포", color="ai_category")
        st.plotly_chart(fig, use_container_width=True)

    conn.close()
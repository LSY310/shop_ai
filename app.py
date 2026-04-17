import streamlit as st
# 웹 화면 만들기 위한 라이브러리 파이썬코드만으로 웹 사이트 ui 만들어줌
from chat import ask_llm
#아까 만든 함수 가져오기

st.title("쇼핑몰 AI 어시스턴트") #화면 제목

question = st.text_input("질문을 입력하세요") #입력창 생성

if st.button("질문하기"): # 버튼생성 크릭시 아래 실행
    if question: # 빈값 방지 입력값 있을때 아래 실행
        answer = ask_llm(question) #질문을 gpt한테 보내고 답변 받아옴
        st.write(answer) # 화면에 출력

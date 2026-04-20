import streamlit as st
from chat import ask_llm
import time

# 페이지 설정
st.set_page_config(page_title="쇼핑몰 AI 매니저", page_icon="🛍️")
st.title("🛍️ 쇼핑몰 AI 매니저")
st.caption("고객님의 쇼핑몰 운영을 돕는 스마트 비서입니다.")

# 대화 내역 저장용 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 기존 대화 내역을 화면에 그리기
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 채팅 입력창 (사용자가 말을 거는 곳)
if prompt := st.chat_input("상품 등록이나 매출 분석을 도와드릴까요?"):
    
    # 사용자 메시지 화면에 표시 및 저장
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 에이전트 응답 처리 (로딩 표시 추가)
    with st.chat_message("assistant"):
        # st.status를 사용하면 에이전트가 생각 중임을 시각적으로 보여줍니다.
        with st.status("의도를 분석하고 업무를 처리 중입니다...", expanded=True) as status:
            try:
                st.write("내부 시스템 연결 중...")
                # 실제 LLM 호출
                full_response = ask_llm(prompt)
                
                # 작업 완료 시 상태 업데이트
                status.update(label="업무 완료!", state="complete", expanded=False)
            except Exception as e:
                status.update(label="오류 발생", state="error", expanded=True)
                full_response = "죄송해요, 잠시 연결에 문제가 생겼어요. 다시 시도해 주시겠어요?"

        # 최종 답변 출력
        st.markdown(full_response)
        
        # 답변 저장
        st.session_state.messages.append({"role": "assistant", "content": full_response})
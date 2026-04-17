# chat.py
import google.generativeai as genai
from tools import tools_list  # tools.py에서 리스트 가져오기
from rag import init_vector_db, retrieve_with_embedding # 정책용 RAG

genai.configure(api_key="")

# 1. 정책 DB 초기화 (기존 로직)
policy_db = init_vector_db("data.txt")

# 2. 모델 설정 (tools_list에 get_order_status와 search_and_recommend가 다 들어있음)
model = genai.GenerativeModel(
    model_name="models/gemini-2.5-flash",
    #파이썬 함수 리스트 전달
    tools=tools_list, 
    #페르소나 및 행동지침 설정
    system_instruction="""당신은 쇼핑몰 매니저입니다. 
    1. 주문 상태는 get_order_status를 사용하세요.
    2. 상품 추천은 search_and_recommend를 사용하세요. 반환한 상품들 중 사용자의 질문(의도)과 직접적으로 관련 있는 상품만 골라서 추천 이유와 함께 설명하세요.
    3. 일반 정책은 기존 지식을 활용하되 필요시 도구를 사용하세요. 
    관련 없는 정보는 걸러내고 친절하게 답변하세요."""
)

# 3. 채팅 세션 시작
# Gemini가 함수 실행이 필요하다고 판단하면, 파이썬이 알아서 해당 함수를 실행하고 그 결과값까지 Gemini에게 다시 전달
chat_session = model.start_chat(enable_automatic_function_calling=True)

# 4.대화 실행 루프
def ask_llm(question):
    try:
        # 질문을 던지면 Gemini가 내부적으로 도구 사용 여부를 결정
        response = chat_session.send_message(question)
        return response.text
    except Exception as e:
        return f"에러 발생: {str(e)}"

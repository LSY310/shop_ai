import google.generativeai as genai
from tools import tools_list, extract_order_number  # tools.py에서 리스트 가져오기
from rag import init_vector_db, retrieve_with_embedding # 정책용 RAG
import json
from database import save_chat_log

genai.configure(api_key="")

# 정책 DB 초기화 (기존 로직)
policy_db = init_vector_db("data.txt")

# 업무 수행 전담 모델
agent_model = genai.GenerativeModel(
    model_name="models/gemini-2.5-flash", # 쿼터 에러 방지를 위해 잠시 1.5-flash 권장!
    tools=tools_list, 
    system_instruction="""당신은 서연님의 쇼핑몰 관리 및 운영 업무를 수행하는 아주 유능하고 친절한 'AI 비서 매니저'입니다.

[기본 페르소나]
- 모든 답변은 직접 말하듯 친절하게 하세요. (예: "~해드렸어요", "확인해볼게요!")
- 도구 실행 결과(JSON 등)를 그대로 보여주지 말고, 이해하기 쉽게 문장으로 요약해서 보고하세요.

[도구 사용 및 업무 지침]
1. 매출 분석 및 브리핑:
   - 'analyze_sales_report'를 호출하여 통계 데이터를 가져오고, 이를 바탕으로 현재 판매 상황과 향후 경영 제언을 한 문장 포함하여 설명하세요.

2. 상품 등록 및 DB 저장 (중요 워크플로우):
   - 사용자가 새로운 상품 정보를 주면 먼저 'generate_smartstore_content'를 호출해 마케팅 문구를 생성하세요.
   - 생성된 콘텐츠를 서연님에게 보여준 뒤, "서연님, 이대로 DB에 저장하거나 내부 시스템으로 전송할까요?"라고 다정하게 확인을 받으세요.
   - 승인 시 상황에 맞게 'save_to_db' 혹은 'register_to_internal_system'을 호출하세요.

3. 상품 추천:
   - 'search_and_recommend'를 사용하되, 검색된 상품 중 사용자의 의도와 가장 밀치하는 상품을 골라 추천 사유와 함께 제안하세요.

4. 엑셀 출력:
   - 모든 데이터 처리가 완료되거나 사용자가 업로용 파일을 요청하면 'export_naver_excel'을 호출하세요.

친절하고 전문적인 어조를 유지하며, 불필요한 도구 호출은 지양하세요."""
)

# 판단 전담 모델 (질문을 분류만 함)
router_model = genai.GenerativeModel("models/gemini-2.5-flash")

# 대화 세션 유지 (이전 대화 내용을 기억함)
# Gemini가 함수 실행이 필요하다고 판단하면, 파이썬이 알아서 해당 함수를 실행하고 그 결과값까지 Gemini에게 다시 전달
chat_session = agent_model.start_chat(enable_automatic_function_calling=True)

# 질문 분류기 (Router) 프롬프트
ROUTER_PROMPT = """
당신은 사용자의 질문에서 의도와 주요 정보를 추출하는 라우터입니다.
결과는 반드시 JSON 형식으로만 답변하세요.

[의도 분류]
1. POLICY: 쇼핑몰의 운영 원칙, 배송비, 환불 규정, 위치/주차 안내 등 '문서화된 정보'를 찾는 질문
2. ACTION: 실시간 데이터 조작이나 계산이 필요한 모든 경우. 
   - 예: 주문/배송 상태 조회, 매출 통계 분석, 상품 추천, 콘텐츠 생성 및 DB 저장, 엑셀 파일 출력 등
3. GENERAL: 단순 인사, 시스템 사용법 문의, 혹은 분류하기 어려운 일상 대화

[추출 정보]
- order_number: '20260420-001'과 같은 형식의 번호가 있으면 추출(없으면 null)
- product_name: 언급된 상품명이 있으면 추출(없으면 null)

[주의 사항]
- 질문에 정책 문의와 기능 실행이 섞여 있는 복합 질문의 경우, 반드시 'ACTION'으로 분류하세요.
- 응답은 반드시 아래 JSON 형식만 허용합니다.
{"category": "POLICY", "reason": "이유를 간략히 기술"}
"""

# 대화 실행 루프
def ask_llm(question):
    # 로그에 기록할 변수들 초기화
    category = "UNKNOWN"
    refined_question = question
    full_response = ""
    is_error = 0

    try:
        # 하이브리드 추출: 정규식으로 먼저 주문번호 확인
        regex_order = extract_order_number(question)

        # 라우터가 질문의 의도를 1차 파악
        route_response = router_model.generate_content(f"{ROUTER_PROMPT}\n질문: {question}")
        # JSON 형태만 쏙 뽑아내기 위해 replace와 strip 사용
        #프로그램이 if문으로 분기 처리를 하려면 텍스트보다는 구조화된 데이터(JSON)가 훨씬 정확하기 때문에 json 사용
        route_data = json.loads(route_response.text.replace("```json", "").replace("```", "").strip())
        category = regex_order or route_data.get("category")

        # 라우터가 놓쳐도 정규식이 찾았다면 보완 (Hybrid)
        order_number = regex_order or route_data.get("order_number")

        # 에이전트가 문맥을 놓치지 않게 명시적으로 정보를 주입
        refined_question = question

        if order_number:
            refined_question = f"[시스템 안내: 주문번호 {order_number} 관련 요청임] {question}"

        # 쇼핑몰 운영 정책 (RAG 전용)
        if category == "POLICY":
            # Gemini에게 정책 문서 내용을 주입하며 답변 유도
            context = retrieve_with_embedding(question, policy_db)
            prompt = f"당신은 CS 담당자입니다. 아래 지침을 참고해 답변하세요.\n지침: {context}\n질문:{refined_question}"
            return agent_model.generate_content(prompt).text

        # 시스템 기능 실행 (Function Calling 전용)
        # 여기서 analyze_sales_report, generate_smartstore_content 등이 실행됩니다.
        elif category == "ACTION":
            # 자동 함수 호출이 활성화된 세션에 질문 전달
            # Gemini가 스스로 판단하여 tools_list에 있는 적절한 함수를 실행함
            response = chat_session.send_message(question)
            return response.text

        # [경로 C] 일반 대화
        else:
            return chat_session.send_message(question).text
        
        # [성공 로그 저장]
        save_chat_log(question, category, full_response, refined_question, is_error=0)
        return full_response

    except Exception as e:

        is_error = 1
        error_msg = str(e)
        
        # 쿼터 에러(429) 발생 시 사용자에게 예쁘게 말하기
        if "429" in str(e):
            return "제가 지금 질문을 너무 많이 받아서 잠시 숨이 차네요! 10초만 쉬었다가 다시 말씀해 주시겠어요? ☕"
        
        # 기타 에러 발생 시 부드러운 사과문
        print(f"시스템 로그: {e}") # 개발용 로그
        return "죄송해요, 시스템 연결이 잠시 불안정해요. 다시 한번만 말씀해 주실 수 있을까요? 🙏"

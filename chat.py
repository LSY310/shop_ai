import google.generativeai as genai
from rag import load_data, retrieve

genai.configure(api_key="")

model = genai.GenerativeModel("models/gemini-2.5-flash")

# 데이터 로딩
try:
    docs = load_data()
except Exception as e:
    docs = []
    print(f"데이터 로딩 실패: {e}")


def ask_llm(question):
    try:
        # RAG 검색
        context = retrieve(question, docs)

        # context 비었을 때 처리
        if not context.strip():
            context = "관련된 정보가 없습니다."

        # prompt 생성
        prompt = f"""
        당신은 쇼핑몰 CS 전문가입니다. 아래 제공된 [참고 정보]만을 바탕으로 답변하세요.
        내용이 없으면 정중히 답변을 거절하세요.

        [참고 정보]
        {context}

        질문: {question}
        """

        # API 호출
        response = model.generate_content(prompt)

        # response 검증
        if not response or not hasattr(response, "text"):
            return "응답을 생성하지 못했습니다."

        if not response.text:
            return "빈 응답입니다."

        return response.text

    except Exception as e:
        return f"에러 발생: {str(e)}"
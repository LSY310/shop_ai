import google.generativeai as genai
from rag import init_vector_db, retrieve_with_embedding

genai.configure(api_key="")

model = genai.GenerativeModel("models/gemini-2.5-flash")


# 프로그램 시작 시 DB 초기화 (딱 한 번 실행)
policy_db = init_vector_db("data.txt")


def ask_llm(question):
    try:
        #임베딩 기반 검색 (의미적 검색)
        context = retrieve_with_embedding(question, policy_db)

        #Prompt 구성
        prompt = f"""
        당신은 쇼핑몰 CS 전문가입니다. 아래 제공된 [참고 정보]만을 바탕으로 답변하세요.
        내용이 없으면 정중히 답변을 거절하세요.

        [참고 정보]
        {context}

        질문: {question}
        """

        #Gemini 답변 생성
        response = model.generate_content(prompt)

        # response 검증
        if not response or not hasattr(response, "text"):
            return "응답을 생성하지 못했습니다."

        if not response.text:
            return "빈 응답입니다."

        return response.text

    except Exception as e:
        return f"에러 발생: {str(e)}"
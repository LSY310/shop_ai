import google.generativeai as genai

genai.configure(api_key="")

model = genai.GenerativeModel("models/gemini-2.5-flash")

def ask_llm(question):
    try:
        response = model.generate_content(
            f"쇼핑몰 상담원처럼 짧게 답해라. 질문: {question}"
        )

        print(response)  # 디버깅용

        if response.text:
            return response.text
        else:
            return "응답이 비어있음"

    except Exception as e:
        return f"에러 발생: {e}"
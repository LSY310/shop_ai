## 📌 Day 1 - LLM 기반 쇼핑몰 챗봇 구현

### 🔍 문제 발생
- OpenAI API 대신 Google Gemini 모델(Free Tier) 사용 결정.
- 초기 연동 시 모델 이름 설정 오류로 인해 API 호출 실패.

### 🛠️ 해결 과정
- 공식 문서 확인 후, 실제 사용 가능한 모델 목록을 `curl` 명령어로 직접 조회하여 정확한 모델 경로 확인.

```bash
# 사용 가능한 모델 목록 직접 확인
curl "[https://generativelanguage.googleapis.com/v1/models?key=YOUR_API_KEY](https://generativelanguage.googleapis.com/v1/models?key=YOUR_API_KEY)"

#응답에서 확인한 정확한 모델명을 코드에 적용하여 해결
```

### 💡 배운 점
- 엄격한 모델 검증: Google Gemini API는 모델 ID(예: gemini-1.5-flash)가 정확해야만 작동함.
- 직접 검증의 중요성: 때로는 문서보다 실제 API 응답을 확인하는 것이 가장 빠르고 확실함.
- LLM 구조 이해: API Key → Model Selection → Generate Content로 이어지는 호출 흐름 파악 완료.

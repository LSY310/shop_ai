## 📌 Day 1 - LLM 기반 쇼핑몰 챗봇 구현

- OpenAI API는 유료라 Google Gemini 모델 사용
- 모델 이름 설정 문제로 초기 연동에서 오류 발생
- curl을 사용해 Google Generative Language API에서 사용 가능한 모델 목록 직접 확인

```bash
curl "https://generativelanguage.googleapis.com/v1/models?key=YOUR_API_KEY"
```
#API 응답을 통해 정확한 모델 경로를 확인 후 코드에 적용하여 문제 해결

Google Gemini API는 모델 이름을 매우 엄격하게 검증함
문서만 보는 것보다 실제 API 호출로 확인하는 것이 빠를 수 있음
LLM 호출 구조 (API key → model → generate_content) 이해 완료

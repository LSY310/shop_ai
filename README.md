## 🗓️ Day 1 - LLM 기반 쇼핑몰 챗봇 구현

### 🔍 문제 발생
- OpenAI API 대신 Google Gemini 모델(Free Tier) 사용 결정.
- 초기 연동 시 모델 이름 설정 오류로 인해 API 호출 실패.

### 🛠️ 해결 과정
- 공식 문서 확인 후, 실제 사용 가능한 모델 목록을 `curl` 명령어로 직접 조회하여 정확한 모델 경로 확인.

```bash
# 사용 가능한 모델 목록 직접 확인
curl "[https://generativelanguage.googleapis.com/v1/models?key=YOUR_API_KEY](https://generativelanguage.googleapis.com/v1/models?key=YOUR_API_KEY)"

#응답에서 확인한 정확한 모델명("models/gemini-2.5-flash")을 코드에 적용하여 해결
```

### 💡 배운 점
- 엄격한 모델 검증: Google Gemini API는 모델 ID가 정확해야만 작동함.
- 직접 검증의 중요성: 때로는 문서보다 실제 API 응답을 확인하는 것이 가장 빠르고 확실함.
- LLM 구조 이해: API Key → Model Selection → Generate Content로 이어지는 호출 흐름 파악 완료.

## 🗓️ Day 2 - RAG 시스템 구축 및 검색 알고리즘 고도화

### 🔍 목표
- 쇼핑몰 운영 정책(data.txt)을 기반으로 한 지능형 QA 시스템 구현
- 단순 키워드 검색의 한계를 극복하고 의미 기반(Semantic) 검색으로 성능 개선.

### 🛠️ 해결 과정
1단계: Keyword Matching 기반 RAG (초기 모델)
방식: 사용자의 질문을 단어 단위로 나누고, 해당 단어가 포함된 문장을 문서에서 추출하여 Gemini에게 전달.
문제점: 사용자가 **"택배비 얼마야?"**라고 물었을 때, 문서에 **"배송비"**라는 단어만 있으면 관련 정보를 찾지 못하는 **'동의어 미매칭'** 문제 발생.

2단계: Embedding & Vector DB 기반 RAG (고도화 모델)
해결: **Gemini Embedding Model ("gemini-embedding-001")**을 도입하여 텍스트를 고차원 벡터로 변환.
Vector DB: ChromaDB를 사용하여 정책 데이터를 벡터화하여 저장 및 검색.
결과: 단어가 일치하지 않아도 "택배비"와 "배송비", "돈 돌려줘"와 "환불"의 의미적 유사도를 계산해 관련 정보를 정확히 추출함.

### 💡 배운 점
RAG의 핵심: 단순히 문서를 읽어주는 것이 아니라, 질문의 '의도'와 가장 가까운 '데이터 조각'을 찾아주는 검색 엔진의 성능이 답변의 퀄리티를 결정함.
Vector DB 활용: 비정형 데이터를 효율적으로 관리하고 검색하기 위한 벡터 데이터베이스의 구조와 활용법 습득.
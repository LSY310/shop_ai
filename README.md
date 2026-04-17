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
문제점: 사용자가 "택배비 얼마야?"라고 물었을 때, 문서에 "배송비"라는 단어만 있으면 관련 정보를 찾지 못하는 **'동의어 미매칭'** 문제 발생.

2단계: Embedding & Vector DB 기반 RAG (고도화 모델)
해결: Gemini Embedding Model ("gemini-embedding-001")을 도입하여 텍스트를 고차원 벡터로 변환.
Vector DB: ChromaDB를 사용하여 정책 데이터를 벡터화하여 저장 및 검색.
결과: 단어가 일치하지 않아도 "택배비"와 "배송비", "돈 돌려줘"와 "환불"의 의미적 유사도를 계산해 관련 정보를 정확히 추출함.

### 💡 배운 점
RAG의 핵심: 단순히 문서를 읽어주는 것이 아니라, 질문의 '의도'와 가장 가까운 '데이터 조각'을 찾아주는 검색 엔진의 성능이 답변의 퀄리티를 결정함.
Vector DB 활용: 비정형 데이터를 효율적으로 관리하고 검색하기 위한 벡터 데이터베이스의 구조와 활용법 습득.

## 🗓️ Day 3 - MVP 엔진 완성(Function Calling을 이용한 지능형 에이전트 구현)

### 🔍 목표
- 단순 답변을 넘어 쇼핑몰의 실시간 데이터(주문, 상품)를 직접 다루는 에이전트(Agent) 시스템 구축.
- 정형 데이터(SQL)와 비정형 데이터(Vector)를 동시에 활용하는 하이브리드 지식 체계 완성.

### 🛠️ 해결 과정
- 하이브리드 데이터베이스 아키텍처 설계
정형 데이터(SQLite): 주문 번호, 배송 상태처럼 정확한 수치와 상태 값이 필요한 정보는 관계형 데이터베이스로 관리.
비정형 데이터(ChromaDB): 상품 설명, 추천 사유 등 의미 기반 검색이 필요한 정보는 벡터 데이터베이스로 관리.

- Function Calling(도구 사용) 도입
Gemini에게 get_order_status와 search_and_recommend라는 Python 함수(도구)를 제공.
작동 원리: LLM이 질문을 분석하여 스스로 최적의 도구를 선택하고, 파라미터(주문번호 등)를 추출하여 함수를 실행한 뒤 그 결과를 바탕으로 최종 답변을 구성함.

- 검색 노이즈 필터링 및 페르소나 강화
문제점: 데이터 부족 시 벡터 검색이 관련 없는 상품(예: 옷 요청에 마우스 추천)을 반환하는 현상 발생.
해결: System Instruction을 고도화하여 LLM이 도구로부터 전달받은 로우 데이터 중 질문의 의도와 일치하는 항목만 선별하여 답변하도록 2차 추론 필터링 적용.

### 🚨 Troubleshooting: API Quota Exceeded (HTTP 429 Error)
현상: 반복적인 기능 테스트 및 도구 호출로 인해 Gemini API 할당량 초과 발생.

대응: 지수 백오프(Exponential Backoff) 개념을 학습하고, 테스트 간격 조정 및 도구 단위 유닛 테스트를 통해 API 호출 효율화.

### 💡 배운 점
- Agentic Workflow: LLM은 더 이상 수동적인 답변기가 아니라, 외부 도구를 적재적소에 활용해 문제를 해결하는 '실행 주체'가 될 수 있음을 체득함.
- 데이터 적재적소 배치: 모든 데이터를 RAG로 처리하기보다, 상태값(주문)은 SQL로, 취향(추천)은 Vector DB로 나누어 관리하는 것이 시스템 안정성과 정확도 면에서 훨씬 유리함을 학습.
- Prompt Engineering의 중요성: 도구의 이름과 설명(Docstring)을 얼마나 구체적으로 작성하느냐가 LLM의 도구 선택 정확도를 결정짓는 핵심 변수임을 깨달음.


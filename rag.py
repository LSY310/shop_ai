import google.generativeai as genai
import chromadb
from chromadb.api.types import Documents, Embeddings

def embed_text(text):# Gemini 임베딩 모델을 사용하는 함수
    result = genai.embed_content(
        model="gemini-embedding-001",
        content=text,
        task_type="retrieval_document" # 문서를 저장할 때
    )
    return result['embedding']

def init_vector_db(file_path="data.txt"):# 벡터 DB 초기화 및 데이터 로드
    client = chromadb.Client()
    # 기존 컬렉션이 있으면 지우고 새로 생성 (메모리 모드)
    collection = client.get_or_create_collection(name="shop_policy")
    
    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    
    # 각 줄(문장)을 임베딩해서 DB에 넣기
    for i, line in enumerate(lines):
        embedding = embed_text(line)
        collection.add(
            ids=[str(i)],
            embeddings=[embedding],
            documents=[line]
        )
    return collection

def retrieve_with_embedding(query, collection): # 질문과 가장 유사한 문장 찾아오기
    # 질문을 임베딩 (숫자로 변환)
    query_embedding = genai.embed_content(
        model="gemini-embedding-001",
        content=query,
        task_type="retrieval_query" # 질문을 던질 때
    )['embedding']
    
    # DB에서 가장 유사한 2개 문장 검색
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=2
    )
    
    # 검색된 문장들을 하나로 합쳐서 반환
    return "\n".join(results['documents'][0])
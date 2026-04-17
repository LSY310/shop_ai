def load_data(): #data.txt 불러와서 한줄씩 리스트 만들기
    with open("data.txt", "r", encoding="utf-8") as f:
        return f.readlines()

def retrieve(query, docs): # 질문 단어로 쪼개서 문장에 있는 경우 해당 문장
    results = []

    for doc in docs:
        if any(word in doc for word in query.split()): #질문 단어로 쪼개기
            results.append(doc)

    return "".join(results)
import json
import os
import numpy as np

from dotenv import load_dotenv
from openai import OpenAI

# ====================================
# OpenAI 설정
# ====================================

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# ====================================
# 임베딩된 법령 로드
# ====================================

with open(
    "road_traffic_law_embedding.json",
    "r",
    encoding="utf-8"
) as f:
    docs = json.load(f)

print(f"{len(docs)}개 문서 로드 완료")

# ====================================
# 코사인 유사도
# ====================================

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)

    return np.dot(a, b) / (
        np.linalg.norm(a)
        * np.linalg.norm(b)
    )

# ====================================
# 검색 함수
# ====================================

def search_law(query, top_k=5):

    # 질문 임베딩 생성
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )

    query_embedding = response.data[0].embedding

    results = []

    for doc in docs:

        score = cosine_similarity(
            query_embedding,
            doc["embedding"]
        )

        results.append(
            (score, doc)
        )

    results.sort(
        key=lambda x: x[0],
        reverse=True
    )

    return results[:top_k]


# ====================================
# 테스트
# ====================================

query = "교차로 좌회전"

results = search_law(query)

for rank, (score, doc) in enumerate(results, start=1):

    print("=" * 80)
    print(f"{rank}위")
    print(f"유사도: {score:.4f}")

    print("조문:", doc["article"])
    print("제목:", doc["title"])
    print("내용:", doc["content"][:200])
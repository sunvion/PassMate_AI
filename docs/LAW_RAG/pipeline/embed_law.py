import os
import json
import time
from openai import OpenAI
from dotenv import load_dotenv

# -----------------------------------
# 환경 설정
# -----------------------------------
load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

EMBED_MODEL = "text-embedding-3-small"


# -----------------------------------
# 데이터 로드
# -----------------------------------
with open(
    "../data/processed/road_traffic_law_clean.json",
    "r",
    encoding="utf-8"
) as f:
    docs = json.load(f)


print(f"총 문서 수: {len(docs)}")


# -----------------------------------
# embedding 생성 함수
# -----------------------------------
def get_embedding(text: str):
    try:
        res = client.embeddings.create(
            model=EMBED_MODEL,
            input=text
        )
        return res.data[0].embedding

    except Exception as e:
        print("embedding error:", e)
        return None


# -----------------------------------
# embedding 실행
# -----------------------------------
embedded_docs = []

for i, doc in enumerate(docs):

    content = doc.get("content", "").strip()

    if not content:
        continue

    embedding = get_embedding(content)

    if embedding is None:
        continue

    embedded_docs.append({
        "chunk_id": doc.get("chunk_id"),
        "law_name": doc.get("law_name"),
        "article": doc.get("article"),
        "paragraph": doc.get("paragraph"),
        "title": doc.get("title"),
        "content": content,
        "embedding": embedding
    })

    # API rate limit 방지
    time.sleep(0.05)

    if (i + 1) % 50 == 0:
        print(f"{i+1}개 처리 완료")


# -----------------------------------
# 저장
# -----------------------------------
output_path = "../data/embeddings/road_traffic_law_embedding.json"

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(
        embedded_docs,
        f,
        ensure_ascii=False
    )


print("embedding 완료")
print(f"저장 경로: {output_path}")
print(f"총 embedding 개수: {len(embedded_docs)}")
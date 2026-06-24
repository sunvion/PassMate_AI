import json
import numpy as np
from rank_bm25 import BM25Okapi
from openai import OpenAI
import os

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
# -----------------------------
# OpenAI client
# -----------------------------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -----------------------------
# 데이터 로드
# -----------------------------
with open("../data/processed/road_traffic_law_rag.json", "r", encoding="utf-8") as f:
    docs = json.load(f)

with open("../data/embeddings/road_traffic_law_embedding.json", "r", encoding="utf-8") as f:
    emb_data = json.load(f)


# embedding map (chunk_id -> vector)
emb_map = {
    item["chunk_id"]: np.array(item["embedding"])
    for item in emb_data
}

# -----------------------------
# BM25 준비 (토큰화)
# -----------------------------
def tokenize(text):
    return text.split()

corpus = [tokenize(doc["content"]) for doc in docs]
bm25 = BM25Okapi(corpus)

# -----------------------------
# query expansion (법률 전용)
# -----------------------------
def expand_query(query: str):
    prompt = f"""
너는 법률 검색 확장기다.

사용자 질문을 법률 검색 키워드로 확장해라.

규칙:
- 문장 금지
- 키워드만
- 5~10개

질문:
{query}
"""

    res = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    expanded = res.output_text.split("\n")
    expanded = [x.strip() for x in expanded if x.strip()]
    return expanded


# -----------------------------
# embedding similarity
# -----------------------------
def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def embed(text):
    res = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return np.array(res.data[0].embedding)


# -----------------------------
# reranker (LLM)
# -----------------------------
def rerank(query, candidates):
    prompt = f"""
너는 법률 문서 검색 reranker다.

질문:
{query}

아래 문서들을 관련성 높은 순으로 정렬해라.

반드시 JSON 배열로 chunk_id만 반환:

문서:
"""

    for c in candidates:
        prompt += f"\nchunk_id: {c['chunk_id']}\ncontent: {c['content'][:200]}\n"

    res = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    try:
        return json.loads(res.output_text)
    except:
        return [c["chunk_id"] for c in candidates]


# -----------------------------
# hybrid search
# -----------------------------
def search(query):

    print("\n질문:", query)

    # 1. query expansion
    expanded = expand_query(query)
    print("\n[Expanded Query]")
    print(expanded)

    # 2. BM25 score
    bm25_scores = bm25.get_scores(tokenize(query))

    # 3. embedding score
    q_emb = embed(query)

    emb_scores = []
    for doc in docs:
        v = emb_map.get(doc["chunk_id"])
        if v is None:
            emb_scores.append(0)
        else:
            emb_scores.append(cosine(q_emb, v))

    # 4. normalize + hybrid score
    bm25_scores = np.array(bm25_scores)
    emb_scores = np.array(emb_scores)

    bm25_scores = (bm25_scores - bm25_scores.min()) / (bm25_scores.max() - bm25_scores.min() + 1e-9)
    emb_scores = (emb_scores - emb_scores.min()) / (emb_scores.max() - emb_scores.min() + 1e-9)

    hybrid = 0.5 * bm25_scores + 0.5 * emb_scores

    # 5. top-k 후보
    top_idx = np.argsort(hybrid)[::-1][:20]
    candidates = [docs[i] for i in top_idx]

    # 6. rerank
    ranked_ids = rerank(query, candidates)

    # 7. 출력
    print("\n=== TOP RESULTS ===\n")

    id_to_doc = {d["chunk_id"]: d for d in docs}

    for cid in ranked_ids[:5]:
        d = id_to_doc.get(cid)
        if not d:
            continue

        print("--------------------")
        print("score:", round(float(hybrid[top_idx.tolist().index(docs.index(d))]), 4))
        print(d["article"], d.get("paragraph"))
        print(d["content"][:200])


# -----------------------------
# run
# -----------------------------
if __name__ == "__main__":
    while True:
        q = input("\n질문 입력: ")
        search(q)
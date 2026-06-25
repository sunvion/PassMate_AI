import os
import json
import numpy as np
from rank_bm25 import BM25Okapi
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =========================
# 📌 Docker 기준 경로
# =========================
LAW_PATH = "/app/docs/LAW_RAG/data/processed/road_traffic_law_clean.json"
EMBED_PATH = "/app/docs/LAW_RAG/data/embeddings/road_traffic_law_embedding_clean.json"


# =========================
# 📌 글로벌 캐시
# =========================
docs = None
emb_data = None
bm25 = None
emb_map = None


# =========================
# 📌 데이터 로딩 (핵심)
# =========================
def load_data():
    global docs, emb_data, bm25, emb_map

    if docs is None:
        if not os.path.exists(LAW_PATH):
            raise FileNotFoundError(f"LAW_PATH not found: {LAW_PATH}")

        with open(LAW_PATH, "r", encoding="utf-8") as f:
            docs = json.load(f)

    if emb_data is None:
        if not os.path.exists(EMBED_PATH):
            raise FileNotFoundError(f"EMBED_PATH not found: {EMBED_PATH}")

        with open(EMBED_PATH, "r", encoding="utf-8") as f:
            emb_data = json.load(f)

    # embedding map 생성
    emb_map = {
        d["chunk_id"]: np.array(d["embedding"])
        for d in emb_data
    }

    # BM25 생성 (docs가 반드시 존재해야 함)
    bm25 = BM25Okapi([tokenize(d["content"]) for d in docs])


# =========================
# 📌 유틸 함수
# =========================
def tokenize(text: str):
    return text.split()


def embed(text: str):
    res = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return np.array(res.data[0].embedding)


def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9)


# =========================
# 📌 핵심 RAG 검색 함수
# =========================
def search_law(query: str):
    load_data()  # 🚨 중요: 항상 안전 초기화

    bm25_scores = bm25.get_scores(tokenize(query))
    q_emb = embed(query)

    emb_scores = []
    for d in docs:
        v = emb_map.get(d["chunk_id"])
        emb_scores.append(cosine(q_emb, v) if v is not None else 0)

    bm25_scores = np.array(bm25_scores)
    emb_scores = np.array(emb_scores)

    # normalization (0~1)
    bm25_scores = (bm25_scores - bm25_scores.min()) / (bm25_scores.max() - bm25_scores.min() + 1e-9)
    emb_scores = (emb_scores - emb_scores.min()) / (emb_scores.max() - emb_scores.min() + 1e-9)

    hybrid = 0.5 * bm25_scores + 0.5 * emb_scores

    top_idx = np.argsort(hybrid)[::-1][:5]

    return [
        {
            "chunk_id": docs[i]["chunk_id"],
            "article": docs[i]["article"],
            "content": docs[i]["content"],
            "score": float(hybrid[i])
        }
        for i in top_idx
    ]
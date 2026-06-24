import json
import numpy as np


# -----------------------------------
# 임베딩 데이터 로드
# -----------------------------------
with open(
    "../data/embeddings/road_traffic_law_embedding.json",
    "r",
    encoding="utf-8"
) as f:
    docs = json.load(f)


print(f"총 embedding 문서 수: {len(docs)}")


# -----------------------------------
# 1. embedding 존재 여부 체크
# -----------------------------------
empty_embedding = [
    d for d in docs
    if "embedding" not in d or not d["embedding"]
]

print(f"\n[embedding 없음]")
print(f"개수: {len(empty_embedding)}")


# -----------------------------------
# 2. embedding 차원 체크
# -----------------------------------
dims = [len(d["embedding"]) for d in docs if "embedding" in d and d["embedding"]]

unique_dims = set(dims)

print(f"\n[embedding 차원 종류]")
print(unique_dims)


if len(unique_dims) == 1:
    print(f"✔ 정상 (차원: {list(unique_dims)[0]})")
else:
    print("⚠ 차원 불일치 있음")


# -----------------------------------
# 3. content ↔ embedding 매칭 체크
# -----------------------------------
missing_content = [
    d for d in docs
    if not d.get("content")
]

print(f"\n[content 없음]")
print(f"개수: {len(missing_content)}")


# -----------------------------------
# 4. cosine similarity 테스트
# -----------------------------------
def cosine_sim(a, b):
    a = np.array(a)
    b = np.array(b)

    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


print("\n[유사도 테스트]")

if len(docs) >= 2:

    a = docs[0]
    b = docs[1]

    sim = cosine_sim(a["embedding"], b["embedding"])

    print("doc0:", a["article"], a.get("paragraph"))
    print("doc1:", b["article"], b.get("paragraph"))
    print("similarity:", sim)


# -----------------------------------
# 5. sanity check (random sample)
# -----------------------------------
print("\n[샘플 데이터 확인]")
sample = docs[:3]

for d in sample:
    print("-----")
    print(d["chunk_id"])
    print(d["article"], d.get("paragraph"))
    print("content 길이:", len(d["content"]))
    print("embedding dim:", len(d["embedding"]))
import json

# -----------------------------------
# 데이터 로드
# -----------------------------------
with open(
    "../data/embeddings/road_traffic_law_embedding.json",
    "r",
    encoding="utf-8"
) as f:
    docs = json.load(f)


clean_docs = []

# -----------------------------------
# 기준
# -----------------------------------
MIN_LEN = 20


for doc in docs:

    content = doc.get("content", "").strip()

    # -----------------------------------
    # short chunk 제거
    # -----------------------------------
    if len(content) < MIN_LEN:
        continue

    clean_docs.append(doc)


# -----------------------------------
# 저장
# -----------------------------------
output_path = "../data/embeddings/road_traffic_law_embedding_clean.json"

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(clean_docs, f, ensure_ascii=False)


print(f"정제 전: {len(docs)}")
print(f"정제 후: {len(clean_docs)}")
print("short chunk 최종 제거 완료")
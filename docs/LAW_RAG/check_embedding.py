import json

with open(
    "road_traffic_law_embedding.json",
    "r",
    encoding="utf-8"
) as f:
    docs = json.load(f)

print("문서 수:", len(docs))

print("첫 번째 문서")
print(docs[0].keys())

print("임베딩 차원")
print(len(docs[0]["embedding"]))
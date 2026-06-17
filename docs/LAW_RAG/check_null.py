import json

with open(
    "road_traffic_law_rag.json",
    "r",
    encoding="utf-8"
) as f:
    docs = json.load(f)

print("전체:", len(docs))

print(
    "제목 없음:",
    sum(1 for d in docs if not d["title"])
)

print(
    "내용 없음:",
    sum(1 for d in docs if not d["content"])
)

print(
    "항 없음:",
    sum(1 for d in docs if not d["paragraph"])
)
import json

with open(
    "road_traffic_law_clean.json",
    "r",
    encoding="utf-8"
) as f:
    docs = json.load(f)

lengths = []

for doc in docs:
    lengths.append(len(doc["content"]))

print("문서 수:", len(lengths))
print("평균 길이:", sum(lengths) / len(lengths))
print("최대 길이:", max(lengths))
print("최소 길이:", min(lengths))
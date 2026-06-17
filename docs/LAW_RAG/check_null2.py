import json

with open(
    "road_traffic_law_clean.json",
    "r",
    encoding="utf-8"
) as f:
    docs = json.load(f)

short_docs = [
    d for d in docs
    if len(d["content"]) < 20
]

print("20자 이하:", len(short_docs))

for doc in short_docs[:20]:
    print(doc)
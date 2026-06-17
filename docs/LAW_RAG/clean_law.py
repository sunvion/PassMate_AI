import json
import re

with open(
    "road_traffic_law_rag.json",
    "r",
    encoding="utf-8"
) as f:
    docs = json.load(f)

clean_docs = []

for doc in docs:

    title = doc.get("title")
    content = doc.get("content")

    # ----------------------
    # 제목 없는 문서 제거
    # ----------------------
    if not title:
        continue

    # ----------------------
    # 내용 없는 문서 제거
    # ----------------------
    if not content:
        continue

    content = content.strip()

    # ----------------------
    # 장 / 절 / 관 제거
    # ----------------------
    if re.match(r"^제\d+장", content):
        continue

    if re.match(r"^제\d+절", content):
        continue

    if re.match(r"^제\d+관", content):
        continue

    # ----------------------
    # 개정 정보 제거
    # ----------------------
    content = re.sub(r"<.*?>", "", content)

    doc["content"] = content.strip()

    clean_docs.append(doc)

print(f"정제 전: {len(docs)}")
print(f"정제 후: {len(clean_docs)}")

with open(
    "road_traffic_law_clean.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        clean_docs,
        f,
        ensure_ascii=False,
        indent=2
    )
import json

# -----------------------------------
# 데이터 로드
# -----------------------------------
with open(
    "../data/processed/road_traffic_law_rag.json",
    "r",
    encoding="utf-8"
) as f:
    docs = json.load(f)


cleaned_docs = []
buffer = None


# -----------------------------------
# merge 기준 (RAG 기준)
# -----------------------------------
def is_short(text):
    return len(text.strip()) < 30


# -----------------------------------
# chunk 순회
# -----------------------------------
for doc in docs:

    content = doc.get("content", "")
    content = content.strip()

    if not content:
        continue


    # -----------------------------------
    # short chunk
    # -----------------------------------
    if is_short(content):

        if buffer is None:
            buffer = doc.copy()
        else:
            buffer["content"] += " " + content

        continue


    # -----------------------------------
    # flush buffer
    # -----------------------------------
    if buffer:
        cleaned_docs.append(buffer)
        buffer = None


    cleaned_docs.append(doc)


# -----------------------------------
# 마지막 buffer flush
# -----------------------------------
if buffer:
    cleaned_docs.append(buffer)


# -----------------------------------
# 저장
# -----------------------------------
with open(
    "../data/processed/road_traffic_law_clean.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(cleaned_docs, f, ensure_ascii=False, indent=2)


print(f"정제 전: {len(docs)}")
print(f"정제 후: {len(cleaned_docs)}")
print("short chunk merge 완료")
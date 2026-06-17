import json

# -----------------------------------
# 원본 로드
# -----------------------------------
with open(
    "도로교통법.json",
    "r",
    encoding="utf-8"
) as f:
    law_data = json.load(f)

# -----------------------------------
# 조문 추출
# -----------------------------------
articles = law_data["법령"]["조문"]["조문단위"]

if isinstance(articles, dict):
    articles = [articles]

documents = []

# -----------------------------------
# 조문 순회
# -----------------------------------
for article in articles:

    article_no = article.get("조문번호")
    article_title = article.get("조문제목")

    clauses = article.get("항", [])

    # 항이 없는 경우
    if not clauses:

        documents.append({
            "law_name": "도로교통법",
            "article": f"제{article_no}조",
            "paragraph": None,
            "title": article_title,
            "content": article.get("조문내용")
        })

        continue

    # dict -> list
    if isinstance(clauses, dict):
        clauses = [clauses]

    # 항 순회
    for idx, clause in enumerate(clauses, start=1):

        documents.append({
            "law_name": "도로교통법",
            "article": f"제{article_no}조",
            "paragraph": f"제{idx}항",
            "title": article_title,
            "content": clause.get("항내용")
        })

# -----------------------------------
# 저장
# -----------------------------------
with open(
    "road_traffic_law_rag.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        documents,
        f,
        ensure_ascii=False,
        indent=2
    )

print(f"{len(documents)}개 저장 완료")
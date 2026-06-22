import json
import hashlib

# -----------------------------------
# 설정
# -----------------------------------
INPUT_PATH = "../data/raw/도로교통법.json"
OUTPUT_PATH = "../data/processed/road_traffic_law_rag.json"
LAW_NAME = "도로교통법"


# -----------------------------------
# 로드
# -----------------------------------
with open(INPUT_PATH, "r", encoding="utf-8") as f:
    law_data = json.load(f)


articles = law_data["법령"]["조문"]["조문단위"]

if isinstance(articles, dict):
    articles = [articles]


documents = []


# -----------------------------------
# flatten 핵심
# -----------------------------------
for article in articles:

    article_no = article.get("조문번호")
    article_title = article.get("조문제목")
    clauses = article.get("항", [])


    # -----------------------------
    # 1) 항이 없는 단일 조문
    # -----------------------------
    if not clauses:

        content = article.get("조문내용")

        if content:

            paragraph = None
            idx = 0

            base = f"{LAW_NAME}|{article_no}|{paragraph}|{idx}|{content}"

            chunk_id = hashlib.md5(
                base.encode("utf-8")
            ).hexdigest()[:12]

            documents.append({
                "chunk_id": chunk_id,
                "law_name": LAW_NAME,
                "article": f"제{article_no}조",
                "paragraph": paragraph,
                "title": article_title,
                "content": content.strip()
            })

        continue


    # -----------------------------
    # 2) dict → list 보정
    # -----------------------------
    if isinstance(clauses, dict):
        clauses = [clauses]


    # -----------------------------
    # 3) 항 단위 flatten
    # -----------------------------
    for idx, clause in enumerate(clauses, start=1):

        content = clause.get("항내용") or article.get("조문내용")

        if not content:
            continue

        paragraph = clause.get("항번호", f"제{idx}항")

        base = f"{LAW_NAME}|{article_no}|{paragraph}|{idx}|{content}"

        chunk_id = hashlib.md5(
            base.encode("utf-8")
        ).hexdigest()[:12]

        documents.append({
            "chunk_id": chunk_id,
            "law_name": LAW_NAME,
            "article": f"제{article_no}조",
            "paragraph": paragraph,
            "title": article_title,
            "content": content.strip()
        })


# -----------------------------------
# 저장
# -----------------------------------
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(documents, f, ensure_ascii=False, indent=2)


print(f"총 {len(documents)}개 chunk 생성 완료")
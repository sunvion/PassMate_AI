import json
import os
from dotenv import load_dotenv
from openai import OpenAI

# ==================================================
# .env 파일 읽기
# ==================================================
load_dotenv()

# ==================================================
# OpenAI 클라이언트 생성
# ==================================================
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# ==================================================
# 정제된 법령 JSON 로드
# ==================================================
with open(
    "road_traffic_law_clean.json",
    "r",
    encoding="utf-8"
) as f:
    docs = json.load(f)

print(f"총 문서 수: {len(docs)}")

# ==================================================
# 임베딩 결과 저장 리스트
# ==================================================
embedded_docs = []

# ==================================================
# 문서 하나씩 임베딩 생성
# ==================================================
for idx, doc in enumerate(docs):

    # ------------------------------------------
    # paragraph가 None일 수 있음
    # ------------------------------------------
    paragraph = doc.get("paragraph") or ""

    # ------------------------------------------
    # 임베딩용 텍스트 생성
    # 검색 품질 향상을 위해
    # 법령명 / 조문 / 제목 포함
    # ------------------------------------------
    embedding_text = f"""
문서종류: 법령

법령명: {doc['law_name']}

조문: {doc['article']}

항: {paragraph}

제목: {doc['title']}

내용:
{doc['content']}
"""

    try:
        # ------------------------------------------
        # OpenAI 임베딩 생성
        # text-embedding-3-small
        # 1536 차원
        # ------------------------------------------
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=embedding_text
        )

        embedding = response.data[0].embedding

        # ------------------------------------------
        # 기존 데이터 + 임베딩 추가
        # ------------------------------------------
        embedded_docs.append({
            **doc,
            "embedding": embedding
        })

        print(f"[{idx+1}/{len(docs)}] 완료")

    except Exception as e:
        print(f"에러 발생: {e}")

# ==================================================
# 임베딩 포함 JSON 저장
# ==================================================
with open(
    "road_traffic_law_embedding.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        embedded_docs,
        f,
        ensure_ascii=False
    )

print("저장 완료")
print(f"최종 문서 수: {len(embedded_docs)}")
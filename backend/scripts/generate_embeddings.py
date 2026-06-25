from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from tqdm import tqdm
import psycopg2
import os
import json
from pathlib import Path

# generate_embeddings.py 기준으로 계산
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

print("ENV PATH:", ENV_PATH)
print("ENV EXISTS:", ENV_PATH.exists())

load_dotenv(ENV_PATH)

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

print("USER:", DB_USER)
print("PASSWORD:", DB_PASSWORD)
print("DB:", DB_NAME)

# BGE-M3 모델 로드
print("모델 로딩 중...")
model = SentenceTransformer("BAAI/bge-m3")
print("모델 로딩 완료")

# PostgreSQL 연결
print("DB 연결 중...")

print("USER:", DB_USER)
print("PASSWORD:", DB_PASSWORD)
print("DB:", DB_NAME)

conn = psycopg2.connect(
    host="db",
    port=5432,
    database="pass_cert_db",
    user="postgres",
    password="password123"
)

cur = conn.cursor()

print("DB 연결 성공")

# 아직 임베딩이 없는 문제 조회
cur.execute("""
SELECT
    id,
    question,
    options,
    explanation
FROM questions
WHERE embedding IS NULL
""")

rows = cur.fetchall()

print(f"임베딩 대상 문제 수: {len(rows)}")

# 임베딩 생성 및 저장
for row in tqdm(rows):

    question_id = row[0]
    question = row[1]
    options = row[2]
    explanation = row[3]

    text = f"""
문제:
{question}

보기:
{json.dumps(options, ensure_ascii=False)}

해설:
{explanation if explanation else ""}
"""

    try:
        embedding = model.encode(
            text,
            normalize_embeddings=True
        ).tolist()

        cur.execute("""
        UPDATE questions
        SET embedding = %s
        WHERE id = %s
        """, (
            embedding,
            question_id
        ))

    except Exception as e:
        print(f"[ERROR] question_id={question_id}")
        print(e)

# 저장
conn.commit()

# 확인
cur.execute("""
SELECT COUNT(*)
FROM questions
WHERE embedding IS NOT NULL
""")

count = cur.fetchone()[0]

print(f"\n완료!")
print(f"임베딩 저장된 문제 수: {count}")

cur.close()
conn.close()
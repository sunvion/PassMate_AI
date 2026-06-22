import json
from collections import Counter

# -----------------------------------
# 데이터 로드
# -----------------------------------
with open(
    "../data/processed/road_traffic_law_clean.json",
    "r",
    encoding="utf-8"
) as f:
    docs = json.load(f)


print(f"총 문서 수: {len(docs)}\n")


# -----------------------------------
# 기본 수집
# -----------------------------------
chunk_ids = []
empty_content = []
too_short = []
missing_paragraph = []

content_set = Counter()


# -----------------------------------
# 문서 순회
# -----------------------------------
for doc in docs:

    chunk_id = doc.get("chunk_id")
    content = doc.get("content", "")
    paragraph = doc.get("paragraph")

    # -------------------------
    # 1. content 검증
    # -------------------------
    if not content or not content.strip():
        empty_content.append(chunk_id)
        continue

    content = content.strip()

    # 너무 짧은 chunk (노이즈 필터)
    if len(content) < 20:
        too_short.append(chunk_id)

    # -------------------------
    # 2. paragraph 누락 체크 (정보성)
    # -------------------------
    if paragraph is None:
        missing_paragraph.append(chunk_id)

    # -------------------------
    # 3. chunk_id 수집
    # -------------------------
    chunk_ids.append(chunk_id)

    # -------------------------
    # 4. content 중복 체크 (진짜 중요)
    # -------------------------
    content_set[content] += 1


# -----------------------------------
# chunk_id 중복 (이건 참고용)
# -----------------------------------
id_counter = Counter(chunk_ids)
duplicate_ids = [k for k, v in id_counter.items() if v > 1]


# -----------------------------------
# content 중복 (진짜 RAG 문제)
# -----------------------------------
duplicate_content = [
    (k, v) for k, v in content_set.items() if v > 1
]


# -----------------------------------
# 결과 출력
# -----------------------------------
print("\n[chunk_id 중복]")
print(f"개수: {len(duplicate_ids)}")


print("\n[content 중복 (중요)]")
print(f"개수: {len(duplicate_content)}")


print("\n[content 비어있는 문서]")
print(f"개수: {len(empty_content)}")


print("\n[너무 짧은 chunk]")
print(f"개수: {len(too_short)}")


print("\n[paragraph 없음]")
print(f"개수: {len(missing_paragraph)}")


print("\n======================")
print("검증 완료")
print("======================")

# -----------------------------------
# RAG 판단 기준
# -----------------------------------
if empty_content or too_short:
    print("⚠ 데이터 품질 문제 있음 (embedding 전에 수정 필요)")
elif len(duplicate_content) > 0:
    print("⚠ content 중복 있음 (chunking 구조 확인 필요)")
else:
    print("✅ RAG 데이터 정상 (embedding 진행 가능)")
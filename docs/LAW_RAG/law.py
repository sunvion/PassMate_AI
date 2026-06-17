import requests
import json

API_KEY = "sunday"  # 너 OC 키

# -------------------------
# 1️⃣ 도로교통법 ID 찾기
# -------------------------
search_url = "http://www.law.go.kr/DRF/lawSearch.do"

search_params = {
    "OC": API_KEY,
    "target": "law",
    "type": "JSON",
    "query": "도로교통법"
}

res = requests.get(search_url, params=search_params)
data = res.json()

# 첫 번째 결과에서 ID 추출
law = data["LawSearch"]["law"][0]
law_id = law["법령ID"]

print("법령ID:", law_id)

# -------------------------
# 2️⃣ 법령 본문 가져오기
# -------------------------
law_url = "http://www.law.go.kr/DRF/lawService.do"

law_params = {
    "OC": API_KEY,
    "target": "law",
    "ID": law_id,
    "type": "JSON"
}

res = requests.get(law_url, params=law_params)
law_data = res.json()

# -------------------------
# 3️⃣ JSON 파일 저장
# -------------------------
with open("도로교통법.json", "w", encoding="utf-8") as f:
    json.dump(law_data, f, ensure_ascii=False, indent=2)

print("저장 완료: 도로교통법.json")
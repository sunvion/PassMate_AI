RAG/
│
├─ data/
│   ├─ raw/
│   │    └─ 도로교통법.json
│   │
│   ├─ processed/
│   │    ├─ road_traffic_law_flat.json        ← flatten 결과 (chunk 생성)
│   │    ├─ road_traffic_law_clean.json       ← 정제 결과 (merge/필터)
│   │
│   └─ embeddings/
│        └─ road_traffic_law_embedding.json   ← embedding 결과
│
│
├─ pipeline/
│   ├─ flatten_law.py      ← RAW → CHUNK 구조화
│   ├─ clean_law.py        ← chunk 품질 정제 (short merge / filter)
│   ├─ embed_law.py        ← OpenAI embedding 생성
│   └─ search_law.py       ← (핵심) RAG 검색 엔진
│
│
├─ test/
│   ├─ check_law_data.py        ← chunk 품질 검사
│   ├─ check_embedding.py       ← embedding 검증
│   └─ check_search.py          ← retrieval 테스트 (추천 추가)
│
│
└─ .env
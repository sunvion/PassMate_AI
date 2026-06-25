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

=========

백엔드 API 붙인 파이프라인

C:\src\PassMate_AI\backend\
│
├── main.py
│
├── app/
│   │
│   ├── api/
│   │   ├── api_router.py
│   │   │
│   │   └── v1/
│   │       ├── rag.py
│   │       └── wrong_note.py
│   │
│   ├── services/
│   │   ├── rag/
│   │   │    └── law_rag.py
│   │   │
│   │   ├── wrong_note_service.py
│   │   ├── context_builder.py
│   │   └── llm_service.py
│   │
│   ├── core/
│   ├── db/
│   ├── models/
│   └── schemas/
│
└── docs/
    └── data/
        ├── processed/
        │     └── road_traffic_law_clean.json
        │
        └── embeddings/
              └── road_traffic_law_embedding_clean.json
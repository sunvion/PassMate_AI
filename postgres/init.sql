-- 1. AI 챗봇 및 유사도 검색을 위한 pgvector 확장 기능 활성화
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. 기출문제 및 문제은행 저장을 위한 메인 테이블 생성
CREATE TABLE IF NOT EXISTS questions (
    id BIGSERIAL PRIMARY KEY,
    exam_type VARCHAR(50) NOT NULL,
    subject VARCHAR(100) NOT NULL,
    year INT NULL,
    number INT NOT NULL,
    question TEXT NOT NULL,
    body TEXT NULL,
    options JSONB NOT NULL,
    answer JSONB NOT NULL,
    explanation TEXT NULL,
    points INT DEFAULT 2,
    category VARCHAR(50) NOT NULL,
    question_type VARCHAR(50) NOT NULL,
    image_url VARCHAR(512) NULL,
    video_url VARCHAR(512) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- (필요하다면) pgvector를 활용할 임베딩 저장용 컬럼을 나중에 추가할 수도 있습니다.
-- 예: ALTER TABLE questions ADD COLUMN embedding vector(1536);
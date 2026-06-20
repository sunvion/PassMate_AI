-- 1. AI 챗봇 및 유사도 검색을 위한 pgvector 확장 기능 활성화
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. 사용자 정보를 저장하는 메인 유저 테이블 생성
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,                               -- Auto Increment / 사용자 고유 ID
    provider VARCHAR(50) NOT NULL,                          -- 소셜 로그인 제공자 ('kakao', 'google')
    provider_id VARCHAR(255) NOT NULL,                      -- 소셜 로그인 유저 고유 ID
    nickname VARCHAR(100) NOT NULL UNIQUE,                  -- 사용자 닉네임
    profile_image VARCHAR(512) NULL,                       -- 프로필 이미지 URL 경로
    chat_limit_override INT NULL,                          -- 유저별 일일 AI 챗봇 이용 제한량
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    email VARCHAR(255) NOT NULL UNIQUE                     -- 이메일 주소
);

-- 3. 기출문제 및 문제은행 저장을 위한 메인 테이블 생성
CREATE TABLE IF NOT EXISTS questions (
    id BIGSERIAL PRIMARY KEY,                               -- Auto Increment / 문제 고유 ID
    exam_type VARCHAR(50) NOT NULL,                         -- 시험 종류 ('CS_GENERAL', 'DRIVERS_LICENSE_1')
    subject VARCHAR(100) NOT NULL,                         -- 과목 분류 ('컴퓨터일반', '도로교통법규')
    chapter VARCHAR(100) NULL,                             -- 과목 세부 분류 ('운영체제', '네트워크')
    year INT NULL,                                         -- 출제 연도
    number INT NOT NULL,                                   -- 문항 번호
    question TEXT NOT NULL,                                -- 문제 발문 (질문 본문 메인)
    body TEXT NULL,                                        -- 추가 질문 지문 데이터
    options JSONB NOT NULL,                                -- 보기 목록 (예: {"1": "보기A", "2": "보기B"})
    answer JSONB NOT NULL,                                 -- 정답 목록 (예: 단일 [2], 복수 [1, 4])
    explanation TEXT NULL,                                 -- 해설 데이터
    points INT DEFAULT 2,                                  -- 문항별 배점
    category VARCHAR(50) NOT NULL,                         -- 세부 유형 분류 ('동영상형', '안전표지형')
    question_type VARCHAR(50) NOT NULL,                    -- UI 레이아웃 타입 (NORMAL, BOX_QUESTION 등)
    image_url VARCHAR(512) NULL,                           -- 문제 내 포함된 이미지 경로 (Next.js public 매칭용)
    video_url VARCHAR(512) NULL,                           -- 운전면허 동영상 파일 경로
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. 🆕 [추가] 사용자의 기출문제 풀이 이력을 영구 저장하는 히스토리 테이블 생성
CREATE TABLE IF NOT EXISTS problem_solving_history (
    id BIGSERIAL PRIMARY KEY,                               -- 풀이 기록 고유 번호 (PK)
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,       -- users 테이블 고유 ID 외래키 연동
    question_id BIGINT NOT NULL REFERENCES questions(id) ON DELETE CASCADE, -- questions 테이블 고유 ID 외래키 연동
    selected_option JSONB NOT NULL,                        -- 유저가 마킹한 정답 배열 스냅샷 (예: [3])
    is_correct BOOLEAN NOT NULL,                           -- 정답 여부 (true / false)
    exam_type VARCHAR(50) NOT NULL,                        -- 당시 시험 종류 스냅샷
    year INT NULL,                                         -- 당시 시험 출제 연도 스냅샷
    subject_snapshot VARCHAR(100) NOT NULL,                -- 당시 과목 명칭 스냅샷
    category_snapshot VARCHAR(50) NOT NULL,                -- 당시 세부 카테고리 스냅샷
    time INT NOT NULL,                                     -- 문제를 푸는 데 걸린 시간 (초)
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP -- 제출 일시 (타임존 포함)
);

-- (필요하다면) pgvector를 활용할 임베딩 저장용 컬럼을 나중에 추가할 수도 있습니다.
-- 예: ALTER TABLE questions ADD COLUMN embedding vector(1536);
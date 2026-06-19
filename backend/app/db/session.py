# app/db/session.py
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings 

# 1. SQLAlchemy 데이터베이스 연결 엔진 생성
# settings.DATABASE_URL 구조 예시: postgresql://user:password@localhost:5432/dbname
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # 연결이 유효한지 미리 확인하는 옵션 (연결 끊김 방지)
    echo=False           # 실제 운영 환경에서는 False, SQL 로그를 보려면 True
)

# 2. 개별 데이터베이스 세션을 생성하는 팩토리 클래스
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

# 3. FastAPI 라우터나 CRUD 레이어에서 사용할 의존성(Dependency) 함수
def get_db() -> Generator[Session, None, None]:
    """
    FastAPI의 Depends(get_db)를 통해 데이터베이스 세션을 주입받을 때 사용합니다.
    요청(Request)이 들어올 때 세션을 열고, 처리가 끝나면(Response) 자동으로 닫아줍니다.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
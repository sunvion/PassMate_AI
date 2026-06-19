# app/db/session.py 전체 코드 예시

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings  # 환경 설정 파일 경로에 맞게 수정

# 1. 비동기 엔진 생성 (이미 되어 있을 확률이 높습니다)
engine = create_async_engine(
    settings.DATABASE_URL, # 예: postgresql+asyncpg://...
    echo=True,
)

# 2. [확인] 일반 sessionmaker가 아닌 async_sessionmaker를 사용해야 합니다.
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
)

# 3. 🔥 [핵심 수정] get_db를 반드시 'async def' 형태의 비동기 제너레이터로 변경합니다.
async def get_db():
    """
    비동기 데이터베이스 세션 주입을 위한 의존성 함수
    """
    async with AsyncSessionLocal() as session:
        yield session
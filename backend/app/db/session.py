from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

# 1. 비동기 엔진 생성
# settings.DATABASE_URL은 반드시 비동기 드라이버를 사용해야 합니다. (예: postgresql+asyncpg://...)
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # 상대방이 추가한 옵션: 연결 유효성을 미리 확인하여 끊김 방지
    echo=True,           # 개발 단계에서 SQL 로그를 보기 위해 True 유지 (운영 시 False 추천)
)

# 2. 일반 sessionmaker가 아닌 async_sessionmaker를 사용합니다.
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
)

# 3. FastAPI 라우터나 CRUD 레이어에서 사용할 비동기 의존성(Dependency) 함수
async def get_db():
    """
    FastAPI의 Depends(get_db)를 통해 비동기 데이터베이스 세션을 주입받을 때 사용합니다.
    요청(Request)이 들어올 때 세션을 열고, 처리가 끝나면(Response) 컨텍스트 매니저를 통해 자동으로 닫아줍니다.
    """
    async with AsyncSessionLocal() as session:
        yield session
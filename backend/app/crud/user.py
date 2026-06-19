# backend/app/crud/user.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User

async def get_user_by_email(db: AsyncSession, email: str):
    """
    이메일로 유저 단건 조회 (비동기 방식)
    """
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()

async def create_google_user(db: AsyncSession, email: str, provider_id: str, provider: str = "google"):
    """
    신규 구글 유저 생성 (비동기 방식)
    """
    import uuid
    random_nickname = f"User_{uuid.uuid4().hex[:6]}"
    
    db_user = User(
        email=email, 
        nickname=random_nickname,
        provider=provider,
        provider_id=provider_id
    )
    db.add(db_user)
    await db.commit()         # 💡 주석 수정: 비동기 커밋
    await db.refresh(db_user) # 💡 주석 수정: 비동기 갱신
    return db_user
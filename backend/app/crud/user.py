from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
import uuid
from app.models.user import User

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """
    기능: 회원 가입 여부를 판단하기 위해 DB에 이메일이 존재하는지 조회합니다. (비동기 방식)
    매개변수: db (AsyncSession 객체), email (조회할 이메일 주소)
    """
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()

async def create_google_user(
    db: AsyncSession, 
    email: str, 
    provider_id: str, 
    profile_image: Optional[str] = None, 
    provider: str = "google"
) -> User:
    """
    기능: 신규 구글 소셜 유저 생성 (비동기 방식)
    """
    # 👈 고유한 랜덤 닉네임 생성
    random_suffix = uuid.uuid4().hex[:8]
    random_nickname = f"user_{random_suffix}"
    
    db_user = User(
        email=email, 
        nickname=random_nickname,
        provider=provider,
        provider_id=provider_id,
        profile_image=profile_image  # 상대방이 추가한 프로필 이미지 반영
    )
    db.add(db_user)
    await db.commit()         # 비동기 커밋
    await db.refresh(db_user) # DB에서 생성된 자동 생성 id 및 timestamp 반영 (비동기 갱신)
    return db_user

async def update_user_profile(
    db: AsyncSession, db_user: User, update_data: dict
) -> User:
    """
    기능: 유저의 닉네임 또는 프로필 이미지를 선택적으로 수정합니다.
    """
    if "nickname" in update_data and update_data["nickname"] is not None:
        db_user.nickname = update_data["nickname"]
    if "profile_image" in update_data and update_data["profile_image"] is not None:
        db_user.profile_image = update_data["profile_image"]

    await db.commit()
    await db.refresh(db_user)
    return db_user


async def delete_user_account(db: AsyncSession, db_user: User) -> None:
    """
    기능: 유저 계정을 영구 삭제합니다. 
    (init.sql의 외래키 ON DELETE CASCADE 설정 덕분에 유저가 삭제되면 풀이 이력도 자동 삭제됩니다)
    """
    await db.delete(db_user)
    await db.commit()  # 💡 비동기 반영 필수
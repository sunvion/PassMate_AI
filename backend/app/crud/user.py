from sqlalchemy.orm import Session
from typing import Optional
from app.models.user import User  # 앞서 작성한 SQLAlchemy User 모델
import uuid


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    기능: 회원 가입 여부를 판단하기 위해 DB에 이메일이 존재하는지 조회합니다. 
    매개변수: db (SQLAlchemy 세션 객체), email (조회할 이메일 주소) 
    """
    return db.query(User).filter(User.email == email).first()


def create_google_user(db: Session, email: str, name: str, profile_image: str) -> User:
    # 👈 고유한 랜덤 닉네임 생성 (예: user_a1b2c3d4)
    random_suffix = uuid.uuid4().hex[:8]
    random_nickname = f"user_{random_suffix}"

    db_user = User(
        email=email,
        nickname=random_nickname,  # 자동 생성된 랜덤 닉네임 주입
        profile_image=profile_image
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)  # DB에서 생성된 자동 생성 id 및 timestamp 반영
    return db_user
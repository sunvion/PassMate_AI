# app/db/base.py
from typing import Any
from sqlalchemy.ext.declarative import as_declarative, declared_attr

@as_declarative()
class Base:
    """
    모든 DB 모델(예: app/models/user.py)이 상속받을 베이스 클래스입니다.
    """
    id: Any
    __name__: str

    # 토큰이나 명시적 설정이 없어도 클래스 이름을 기반으로 테이블 이름을 자동으로 생성해 줍니다.
    # 예: class User(Base) -> 테이블 이름: user
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
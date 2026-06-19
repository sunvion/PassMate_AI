from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr

# 가입 시점에는 프론트엔드로부터 닉네임을 받지 않음 (서버가 자동 생성)
class UserCreate(UserBase):
    pass

class UserMe(UserBase):
    nickname: str
    picture: Optional[str] = Field(None, validation_alias="profile_image", serialization_alias="picture")

    class Config:
        from_attributes = True
        populate_by_name = True 

class UserResponse(UserBase):
    id: int
    nickname: str
    profile_image: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
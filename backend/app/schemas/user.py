# backend/app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr

# 가입 시점에는 프론트엔드로부터 닉네임을 받지 않음 (서버가 자동 생성)
class UserCreate(UserBase):
    pass

# 🆕 [추가] 닉네임 및 프로필 수정을 프론트엔드에서 요청할 때 사용하는 스키마
class UserUpdateRequest(BaseModel):
    nickname: Optional[str] = None
    # 💡 프론트엔드가 'picture'라는 필드명으로 보내도 'profile_image'로 안전하게 매핑되도록 처리합니다.
    profile_image: Optional[str] = Field(None, validation_alias="picture")

class UserMe(UserBase):
    nickname: str
    picture: Optional[str] = Field(None, validation_alias="profile_image", serialization_alias="picture")

    class Config:
        from_attributes = True
        populate_by_name = True 

# 🔄 [보완] 정보 수정(PUT) 후 결과 리턴 시에도 UserMe처럼 picture 형식을 유지하고 싶다면 
# 라우터에서 response_model로 이 UserResponse를 사용하면 됩니다.
class UserResponse(UserBase):
    id: int
    nickname: str
    # 💡 프론트가 'picture'라는 일관된 필드명으로 받아볼 수 있도록 앨리어싱 설정을 추가해 줍니다.
    picture: Optional[str] = Field(None, validation_alias="profile_image", serialization_alias="picture")
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True # 💡 필드명 앨리어스(picture) 생성을 활성화하기 위해 추가
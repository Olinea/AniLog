from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    """用户登录请求模型"""
    email: EmailStr
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    }

class UserResponse(UserBase):
    """用户响应模型，排除敏感信息"""
    id: int
    openid: Optional[str] = None
    avatarUrl: Optional[str] = None
    manager: Optional[int] = 0
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    }

class UserInDB(User):
    hashed_password: str

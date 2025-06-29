from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CatBase(BaseModel):
    name: str = Field(..., min_length=1)
    nickname: Optional[str] = None
    gender: Optional[str] = None
    characteristics: Optional[str] = None
    campus: Optional[str] = None
    area: Optional[str] = None
    habit: Optional[str] = None
    is_active: bool = True

class CatCreate(CatBase):
    pass

class Cat(CatBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

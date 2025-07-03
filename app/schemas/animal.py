from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .photo import Photo

class AnimalBase(BaseModel):
    name: str = Field(..., min_length=1)
    nickname: Optional[str] = None
    gender: Optional[str] = None
    characteristics: Optional[str] = None
    campus: Optional[str] = None
    area: Optional[str] = None
    habit: Optional[str] = None
    is_active: bool = True

class AnimalCreate(AnimalBase):
    pass

class Animal(AnimalBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    best_photo: Optional[Photo] = None

    class Config:
        from_attributes = True

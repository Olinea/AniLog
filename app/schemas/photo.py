from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PhotoBase(BaseModel):
    animal_id: int = Field(..., description="关联的动物的ID")
    photo_id: str = Field(..., description="OSS或其他外部系统的图片ID")
    photo_file_id: Optional[str] = Field(None, description="OSS或其他外部系统的文件ID")
    shooting_date: Optional[datetime] = Field(None, description="拍摄日期")
    verified: bool = Field(False, description="是否已验证")
    best: bool = Field(False, description="是否是最佳图片")

class PhotoCreate(PhotoBase):
    # 创建时不需要提供 user_id, verified, best, created_at, updated_at, id
    pass

class PhotoUpdate(BaseModel):
    # 更新时可以只提供部分字段
    animal_id: Optional[int] = Field(None, description="关联的动物的ID")
    photo_id: Optional[str] = Field(None, description="OSS或其他外部系统的图片ID")
    photo_file_id: Optional[str] = Field(None, description="OSS或其他外部系统的文件ID")
    shooting_date: Optional[datetime] = Field(None, description="拍摄日期")
    verified: Optional[bool] = Field(None, description="是否已验证")
    best: Optional[bool] = Field(None, description="是否是最佳图片")

class Photo(PhotoBase):
    id: int
    user_id: int # 上传者ID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PhotoBase(BaseModel):
    animal_id: int = Field(..., description="关联的动物的ID")
    photo_url: str = Field(..., description="OSS或其他外部系统的url")
    photo_file_id: Optional[str] = Field(None, description="OSS或其他外部系统的文件ID/阿里云etag")
    shooting_date: Optional[datetime] = Field(None, description="拍摄日期")
    verified: bool = Field(False, description="是否已验证")
    best: bool = Field(False, description="是否是最佳图片")

class PhotoCreate(PhotoBase):
    # 创建时不需要提供 user_id, verified, best, created_at, updated_at, id
    pass


class Photo(PhotoBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OSSCredentials(BaseModel):
    """OSS 直传凭证"""
    accessId: str = Field(..., description="AccessKey ID")
    host: str = Field(..., description="OSS 主机地址")
    policy: str = Field(..., description="Base64 编码的策略")
    signature: str = Field(..., description="签名")
    expire: int = Field(..., description="过期时间戳")
    callback: str = Field(..., description="Base64 编码的回调配置")
    dir: str = Field(..., description="上传目录")


class PermissionCredentials(BaseModel):
    """权限管理凭证"""
    accessId: str = Field(..., description="AccessKey ID")
    host: str = Field(..., description="OSS 主机地址")
    policy: str = Field(..., description="Base64 编码的策略")
    signature: str = Field(..., description="签名")
    expire: int = Field(..., description="过期时间戳")
    dir: str = Field(..., description="允许操作的目录")
    permissions: list[str] = Field(..., description="权限列表：read, write, delete")
    callback: str = Field(..., description="Base64 编码的回调配置")


class OSSCallback(BaseModel):
    """OSS 回调数据"""
    object: str = Field(..., description="文件路径")
    size: str = Field(..., description="文件大小")
    mimeType: str = Field(..., description="MIME 类型")
    etag: str = Field(..., description="文件 ETag")
    animal_id: str = Field(..., description="动物 ID")


class PhotoFromOSS(BaseModel):
    """从 OSS 回调创建的照片数据"""
    animal_id: int = Field(..., description="关联的动物的ID")
    photo_url: str = Field(..., description="OSS 文件 URL")
    photo_file_id: str = Field(..., description="OSS 文件 ETag")

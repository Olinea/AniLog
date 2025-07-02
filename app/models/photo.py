from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base

class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    animal_id = Column(Integer, ForeignKey("animals.id"), index=True) # 外键关联 Animal 表
    photo_url = Column(String(255), unique=True, index=True) # OSS图片URL
    photo_file_id = Column(String(255), nullable=True) # OSS或其他外部系统的文件ID / 阿里云的etag
    user_id = Column(Integer, ForeignKey("users.id"), index=True) # 外键关联 User 表 (上传者)
    verified = Column(Boolean, default=False) # 是否已验证 / 是后期管理员审核通过的图片
    shooting_date = Column(DateTime(timezone=True), nullable=True) # 拍摄日期 / 图片拍摄时间，由用户定义上传
    best = Column(Boolean, default=False) # 是否是最佳图片/管理员标记的图片
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 建立与 Animal 和 User 模型的关系
    animal = relationship("Animal", back_populates="photos")
    uploader = relationship("User", back_populates="photos")

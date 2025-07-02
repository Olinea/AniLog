from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship # 导入 relationship

from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(100))
    openid = Column(String(255), unique=True, index=True, nullable=True)
    avatarUrl = Column(String(255), nullable=True)
    manager = Column(Integer, nullable=True, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 添加与 Photo 模型的关系
    photos = relationship("Photo", back_populates="uploader")
    
    # 注意：已删除对不存在的 Item 模型的引用

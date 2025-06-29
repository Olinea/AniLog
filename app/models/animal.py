from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship # 导入 relationship

from app.db.database import Base

class Animal(Base):
    __tablename__ = "animals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, unique=True)
    nickname = Column(String(100), nullable=True)
    gender = Column(String(10), nullable=True) # 例如: 'male', 'female', 'unknown'
    characteristics = Column(Text, nullable=True)
    campus = Column(String(50), nullable=True)
    area = Column(String(50), nullable=True)
    habit = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 添加与 Photo 模型的关系
    photos = relationship("Photo", back_populates="animal")

from sqlalchemy.orm import relationship

from app.models.user import User

# 添加关系到User模型
User.items = relationship("Item", back_populates="owner")

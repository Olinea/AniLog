from sqlalchemy.orm import relationship

from app.models.user import User
from app.models.animal import Animal
from app.models.photo import Photo

# 添加关系到User模型 (已存在)
User.items = relationship("Item", back_populates="owner")

# 添加关系到 Animal 模型
Animal.photos = relationship("Photo", back_populates="animal")

# 添加关系到 User 模型 (上传者)
User.photos = relationship("Photo", back_populates="uploader")

from sqlalchemy.orm import relationship

from app.models.user import User
from app.models.item import Item  # 导入 Item 模型
from app.models.animal import Animal  # 导入 Animal 模型
from app.models.photo import Photo  # 导入 Photo 模型

# 添加关系到User模型 (已存在)
User.items = relationship("Item", back_populates="owner")

# 添加关系到 Animal 模型
Animal.photos = relationship("Photo", back_populates="animal")

# 添加关系到 User 模型 (上传者)
User.photos = relationship("Photo", back_populates="uploader")

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 数据库连接配置
DATABASE_URL = "mysql+pymysql://fastapi:Wwtc26iKWA2BxRXp@23.158.24.109/fastapi"

# 创建数据库引擎
engine = create_engine(DATABASE_URL)

# 创建会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建Base类
Base = declarative_base()

# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 创建所有表
def create_tables():
    Base.metadata.create_all(bind=engine)

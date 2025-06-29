import os
from typing import Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class DatabaseConfig:
    """数据库配置类"""
    
    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = int(os.getenv("DB_PORT", "3306"))
        self.name = os.getenv("DB_NAME", "fastapi")
        self.user = os.getenv("DB_USER", "root")
        self.password = os.getenv("DB_PASSWORD", "")
        self.driver = os.getenv("DB_DRIVER", "mysql+pymysql")
        
    @property
    def url(self) -> str:
        """构建数据库连接URL"""
        # 优先使用环境变量中的完整URL
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            return database_url
            
        # 否则从单独的配置项构建URL
        return f"{self.driver}://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
    
    def __str__(self) -> str:
        """返回不包含密码的连接信息"""
        return f"{self.driver}://{self.user}:***@{self.host}:{self.port}/{self.name}"

class AppConfig:
    """应用配置类"""
    
    def __init__(self):
        self.debug = os.getenv("DEBUG", "False").lower() == "true"
        self.secret_key = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
        self.algorithm = os.getenv("ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        
        # 数据库配置
        self.database = DatabaseConfig()

# 创建全局配置实例
config = AppConfig()

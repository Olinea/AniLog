from typing import Optional
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class DatabaseConfig(BaseSettings):
    """数据库配置类"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    host: str = Field(default="localhost", alias="DB_HOST")
    port: int = Field(default=3306, alias="DB_PORT")
    name: str = Field(default="fastapi", alias="DB_NAME")
    user: str = Field(default="root", alias="DB_USER")
    password: str = Field(default="", alias="DB_PASSWORD")
    driver: str = Field(default="mysql+pymysql", alias="DB_DRIVER")
    database_url: Optional[str] = Field(default=None, alias="DATABASE_URL")

    @computed_field
    @property
    def url(self) -> str:
        """构建数据库连接URL"""
        # 优先使用环境变量中的完整URL
        if self.database_url:
            connection_url = self.database_url
            print(f"使用环境变量中的完整数据库URL: {self.database_url.replace(self.password, '***') if self.password else self.database_url}")
            return connection_url

        url_obj = URL.create(
            drivername=self.driver,
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.name
        )
        print(f"数据库连接信息: {self.__str__()}")
        return str(url_obj)

    def __str__(self) -> str:
        """返回不包含密码的连接信息"""
        url_obj = URL.create(
            drivername=self.driver,
            username=self.user,
            password="***",
            host=self.host,
            port=self.port,
            database=self.name
        )
        return str(url_obj)


class OSSConfig(BaseSettings):
    """阿里云 OSS 配置类"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    access_key_id: str = Field(default="", alias="ALI_AK_ID")
    access_key_secret: str = Field(default="", alias="ALI_AK_SECRET")
    host: str = Field(default="https://ainlog233.oss-cn-wuhan-lr.aliyuncs.com", alias="OSS_HOST")
    bucket: str = Field(default="ainlog233", alias="OSS_BUCKET")
    dir_prefix: str = Field(default="user/", alias="OSS_DIR_PREFIX")
    callback_url: str = Field(default="http://127.0.0.1:8000/api/photos/oss-callback", alias="OSS_CALLBACK_URL")


class AppConfig(BaseSettings):
    """应用配置类"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    debug: bool = Field(default=False, alias="DEBUG")
    secret_key: str = Field(
        default="your-secret-key-change-in-production", 
        alias="SECRET_KEY"
    )
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30, 
        alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    @computed_field
    @property
    def database(self) -> DatabaseConfig:
        """数据库配置"""
        return DatabaseConfig()

    @computed_field
    @property
    def oss(self) -> OSSConfig:
        """OSS 配置"""
        return OSSConfig()


# 创建全局配置实例
config = AppConfig()

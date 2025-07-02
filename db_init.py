"""
数据库初始化脚本
"""
import logging
from sqlalchemy import inspect

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 导入所有模型以确保它们被SQLAlchemy注册
from app.models.user import User
from app.models.animal import Animal
from app.models.photo import Photo
from app.db.database import create_tables, engine, Base

def check_db_connection():
    """检查数据库连接"""
    try:
        conn = engine.connect()
        logger.info("成功连接到数据库!")
        conn.close()
        return True
    except Exception as e:
        logger.error(f"数据库连接失败: {str(e)}")
        return False

def show_db_config():
    """显示数据库配置信息"""
    from app.config import config
    logger.info(f"数据库配置: {config.database}")

def check_tables():
    """检查表是否存在"""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    logger.info(f"现有数据库表: {tables}")
    
    # 列出所有模型定义的表
    model_tables = [table.__tablename__ for table in Base.__subclasses__()]
    logger.info(f"模型定义的表: {model_tables}")
    
    # 检查哪些表缺失
    missing_tables = [table for table in model_tables if table not in tables]
    if missing_tables:
        logger.warning(f"缺失的表: {missing_tables}")
    else:
        logger.info("所有模型表都已在数据库中创建")

def initialize_db():
    """初始化数据库"""
    if check_db_connection():
        try:
            # 检查现有表
            check_tables()
            
            # 创建表
            logger.info("开始创建数据库表...")
            create_tables()
            logger.info("数据库表创建成功!")
            
            # 检查创建后的表
            check_tables()
        except Exception as e:
            logger.error(f"创建表失败: {str(e)}")

if __name__ == "__main__":
    show_db_config()
    initialize_db()

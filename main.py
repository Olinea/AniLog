from app.routers import auth, users, photos, animals
from app.db.database import create_tables, engine
from app.models import User, Animal, Photo
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 确保首先导入所有模型


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    try:
        with engine.connect() as conn:
            logger.info("数据库连接成功")
        logger.info("创建数据库表...")
        create_tables()
        logger.info("数据库表创建完成")
    except Exception as e:
        logger.error(f"启动错误: {e}")

    yield
    logger.info("应用关闭")

app = FastAPI(
    title="FastAPI模板",
    description="包含用户验证、Cookie和MySQL功能的FastAPI应用",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中，应明确设置允许的源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局异常处理


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "服务器内部错误", "detail": str(exc)}
    )

# 路由注册
app.include_router(auth.router, prefix="/api", tags=["认证"])
app.include_router(users.router, prefix="/api/users", tags=["用户"])
app.include_router(photos.router, prefix="/api/photos", tags=["图片"])
app.include_router(animals.router, prefix="/api/animals", tags=["动物"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

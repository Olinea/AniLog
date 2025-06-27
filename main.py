from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, users, items
from app.db.database import create_tables

app = FastAPI(
    title="FastAPI模板",
    description="包含用户验证、Cookie和MySQL功能的FastAPI应用",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中，应明确设置允许的源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api", tags=["认证"])
app.include_router(users.router, prefix="/api/users", tags=["用户"])
app.include_router(items.router, prefix="/api/items", tags=["项目"])

# 创建数据库表
create_tables()

@app.get("/")
async def root():
    return {"message": "欢迎使用FastAPI模板！"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

# FastAPI 模板

这是一个包含用户验证、Cookie和MySQL的FastAPI模板项目。

## 特性

- 用户认证（登录/注册/注销）
- JWT令牌和Cookie认证
- 基于MySQL的数据存储
- 项目CRUD操作
- 依赖注入
- Pydantic模型验证

## 项目结构

```
fastapi/
├── app/
│   ├── db/
│   │   └── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── item.py
│   ├── routers/
│   │   ├── auth.py
│   │   ├── users.py
│   │   └── items.py
│   ├── schemas/
│   │   ├── user.py
│   │   └── item.py
│   └── utils/
│       └── auth.py
├── main.py
└── requirements.txt
```

## 安装

1. 克隆仓库：

```
git clone <仓库地址>
cd fastapi
```

2. 安装依赖：

```
pip install -r requirements.txt
```

3. 设置数据库：

编辑 `app/db/database.py` 文件中的数据库连接字符串，将其替换为您的MySQL数据库配置：

```python
DATABASE_URL = "mysql+pymysql://username:password@localhost/fastapi_db"
```

4. 运行应用：

```
uvicorn main:app --reload
```

## API文档

启动应用后，可以访问以下地址查看API文档：

- Swagger UI：http://localhost:8000/docs
- ReDoc：http://localhost:8000/redoc

## 使用方法

### 认证

- 注册新用户：POST `/api/users/`
- 用户登录：POST `/api/login`
- 用户登出：POST `/api/logout`
- 获取当前用户信息：GET `/api/me`

### 用户管理

- 获取用户列表：GET `/api/users/`
- 获取特定用户：GET `/api/users/{user_id}`

### 项目管理

- 创建新项目：POST `/api/items/`
- 获取项目列表：GET `/api/items/`
- 获取特定项目：GET `/api/items/{item_id}`
- 更新项目：PUT `/api/items/{item_id}`
- 删除项目：DELETE `/api/items/{item_id}`

## 安全说明

在生产环境中，请确保：

1. 替换 `app/utils/auth.py` 中的 `SECRET_KEY` 为安全的随机字符串
2. 配置合适的CORS设置
3. 使用HTTPS
4. 限制敏感操作的速率

## 许可证

MIT

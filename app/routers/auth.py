from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from typing import Optional
from fastapi.responses import JSONResponse

from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserInDB
from app.utils.auth import (
    verify_password,
    create_access_token,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter()

# 定义OAuth2密码承载器 (不再用于get_current_user，但保留以供login使用)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

def get_user(db: Session, username: str):
    """根据用户名获取用户"""
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    """验证用户"""
    user = get_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

async def get_current_user(
    session_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
) -> Optional[User]: # 修改返回类型提示为 Optional[User]
    """获取当前用户"""
    token_to_use = session_token

    if token_to_use is None:
        return None

    try:
        payload = jwt.decode(token_to_use, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None

    user = get_user(db, username=username)
    if user is None:
        return None

    return user

async def get_required_user(current_user: User = Depends(get_current_user)) -> User:
    """获取当前用户 (如果未认证则抛出 401)"""
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未认证",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user

@router.post("/login")
async def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """用户登录"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # 设置cookie
    response.set_cookie(
        key="session_token",
        value=access_token,
        httponly=True,  # 防止JavaScript访问
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",  # 防止CSRF
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout(response: Response):
    """用户登出"""
    response.delete_cookie(key="session_token")
    return {"message": "成功登出"}

@router.get("/me")
async def read_users_me(current_user: Optional[User] = Depends(get_current_user)):
    """获取当前用户信息"""
    if current_user is None:
        # 如果认证失败 (current_user 为 None)，返回特定数据和 401 状态码
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Authentication failed", "code": 401} # 返回特定数据
        )
    return current_user

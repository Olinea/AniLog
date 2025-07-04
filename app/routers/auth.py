from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie, Request, Header
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from typing import Optional
from fastapi.responses import JSONResponse
from app.schemas.user import User as UserSchema, UserResponse

from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserInDB, UserLogin
from app.utils.auth import (
    verify_password,
    create_access_token
)
from app.config import config

router = APIRouter()

# 标准OAuth2密码承载器
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login", auto_error=False)
# HTTP Bearer认证方案
bearer_scheme = HTTPBearer(auto_error=False)


def get_user(db: Session, email: str):
    """根据邮箱获取用户"""
    return db.query(User).filter(User.email == email).first()


def authenticate_user(db: Session, email: str, password: str):
    """验证用户"""
    user = get_user(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user


def get_token_from_request(
    session_token: Optional[str] = Cookie(None),
    authorization: Optional[HTTPAuthorizationCredentials] = Depends(
        bearer_scheme),
    oauth2_token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[str]:
    """
    从请求中获取令牌，优先级：
    1. Cookie中的session_token
    2. Authorization头部的Bearer令牌
    3. OAuth2自动提取的令牌
    """
    # 优先使用Cookie中的令牌
    if session_token:
        return session_token

    # 其次使用Authorization头部的Bearer令牌
    if authorization and authorization.credentials:
        return authorization.credentials

    # 最后使用OAuth2自动提取的令牌
    if oauth2_token:
        return oauth2_token

    return None


async def get_current_user(
    token: Optional[str] = Depends(get_token_from_request),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """获取当前用户"""
    if token is None:
        return None

    try:
        payload = jwt.decode(token, config.secret_key,
                             algorithms=[config.algorithm])
        email = payload.get("sub")
        if email is None:
            return None
    except JWTError:
        return None

    user = get_user(db, email=email)
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
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """用户登录 - 使用邮箱和密码"""
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(
        minutes=config.access_token_expire_minutes)
    access_token = create_access_token(
        # 使用email作为token的sub
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    # 设置cookie
    response.set_cookie(
        key="session_token",
        value=access_token,
        httponly=True,  # 防止JavaScript访问
        max_age=config.access_token_expire_minutes * 60,
        samesite="lax",  # 防止CSRF
    )

    # 转换为 Pydantic 模型以排除敏感信息

    user_data = UserResponse.model_validate(user)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data
    }


@router.post("/logout")
async def logout(response: Response):
    """用户登出"""
    response.delete_cookie(key="session_token")
    return {"message": "成功登出"}


@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_required_user)):
    """验证并获取当前登录用户信息"""
    user_data = UserResponse.model_validate(current_user)
    return {"user": user_data}

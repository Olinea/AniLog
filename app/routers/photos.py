from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
import base64
import json
import hmac
import hashlib
from datetime import datetime, timedelta

from app.db.database import get_db
from app.models.user import User
from app.models.animal import Animal
from app.models.photo import Photo
from app.schemas.photo import PhotoCreate, Photo as PhotoSchema, OSSCredentials, OSSCallback, PhotoFromOSS
from app.routers.auth import get_current_user, get_required_user
from app.config import config

router = APIRouter()


def check_manager_permission(current_user: User = Depends(get_required_user)):
    """检查当前用户是否有 manager >= 3 的权限"""
    manager_value = getattr(current_user, "manager", None)
    if manager_value is None or int(manager_value) < 3:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限",
        )
    return current_user


@router.get("/oss-credentials", response_model=OSSCredentials)
async def get_oss_credentials(
    animal_id: int,
    current_user: User = Depends(get_required_user),
    db: Session = Depends(get_db)
):
    """获取 OSS 直传凭证"""
    
    # 检查关联的动物是否存在
    animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if animal is None:
        raise HTTPException(status_code=404, detail="关联的动物不存在")
    
    # OSS 配置
    oss_config = config.oss
    
    # 上传目录：user/{user_id}/
    upload_dir = f"{oss_config.dir_prefix}{current_user.id}/"
    
    # 策略有效时间（5分钟）
    expire_time = 300
    expiration = datetime.utcnow() + timedelta(seconds=expire_time)
    expiration_iso = expiration.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    
    # 1. 定义并编码上传回调参数
    callback_object = {
        "callbackUrl": oss_config.callback_url,
        "callbackBody": f"object=${{object}}&size=${{size}}&mimeType=${{mimeType}}&etag=${{etag}}&animal_id={animal_id}",
        "callbackBodyType": "application/x-www-form-urlencoded"
    }
    base64_callback = base64.b64encode(json.dumps(callback_object).encode()).decode()
    
    # 2. 定义上传策略
    policy = {
        "expiration": expiration_iso,
        "conditions": [
            ["content-length-range", 0, 10485760],  # 10MB
            ["starts-with", "$key", upload_dir],
            {"callback": base64_callback}
        ]
    }
    base64_policy = base64.b64encode(json.dumps(policy).encode()).decode()
    
    # 3. 生成签名
    signature = base64.b64encode(
        hmac.new(
            oss_config.access_key_secret.encode(),
            base64_policy.encode(),
            hashlib.sha1
        ).digest()
    ).decode()
    
    # 4. 返回凭证信息
    return OSSCredentials(
        accessId=oss_config.access_key_id,
        host=oss_config.host,
        policy=base64_policy,
        signature=signature,
        expire=int((datetime.utcnow() + timedelta(seconds=expire_time - 10)).timestamp()),
        callback=base64_callback,
        dir=upload_dir
    )


@router.post("/oss-callback", response_model=dict)
async def oss_callback(
    request: Request,
    db: Session = Depends(get_db)
):
    """处理 OSS 上传成功回调"""
    
    # 获取表单数据
    form_data = await request.form()
    
    try:
        # 安全地获取字符串值
        def get_form_value(key: str) -> str:
            value = form_data.get(key)
            if isinstance(value, str):
                return value
            elif value is None:
                raise ValueError(f"Missing required field: {key}")
            else:
                raise ValueError(f"Invalid type for field {key}")
        
        callback_data = OSSCallback(
            object=get_form_value("object"),
            size=get_form_value("size"),
            mimeType=get_form_value("mimeType"),
            etag=get_form_value("etag"),
            animal_id=get_form_value("animal_id")
        )
        
        # 验证动物是否存在
        animal_id = int(callback_data.animal_id)
        animal = db.query(Animal).filter(Animal.id == animal_id).first()
        if not animal:
            raise HTTPException(status_code=400, detail="关联的动物不存在")
        
        # 从文件路径中提取用户ID
        # 假设路径格式为 user/{user_id}/filename
        path_parts = callback_data.object.split('/')
        if len(path_parts) >= 2 and path_parts[0] == "user":
            user_id = int(path_parts[1])
        else:
            raise HTTPException(status_code=400, detail="无效的文件路径格式")
        
        # 构建完整的图片URL
        photo_url = f"{config.oss.host}/{callback_data.object}"
        
        # 检查是否已存在相同的照片
        existing_photo = db.query(Photo).filter(
            Photo.photo_url == photo_url
        ).first()
        
        if not existing_photo:
            # 创建新的照片记录
            db_photo = Photo(
                animal_id=animal_id,
                photo_url=photo_url,
                photo_file_id=callback_data.etag,
                user_id=user_id,
                verified=False,
                best=False
            )
            
            db.add(db_photo)
            db.commit()
            db.refresh(db_photo)
        
        return {"status": "ok"}
        
    except Exception as e:
        print(f"OSS callback error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"处理回调失败: {str(e)}")


@router.post("/", response_model=PhotoSchema, status_code=status.HTTP_201_CREATED)
async def create_photo(
    photo: PhotoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user)
):
    """上传新动物图片"""

    # 检查关联的动物是否存在
    animal = db.query(Animal).filter(Animal.id == photo.animal_id).first()
    if animal is None:
        raise HTTPException(status_code=404, detail="关联的动物不存在")

    # 检查 photo_url 是否已存在 (假设 photo_url 在外部系统中是唯一的)
    existing_photo = db.query(Photo).filter(
        Photo.photo_url == photo.photo_url).first()
    if existing_photo:
        raise HTTPException(status_code=400, detail="图片ID已存在")

    db_photo = Photo(
        **photo.dict(exclude={'verified', 'best'}),
        user_id=current_user.id
    )

    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)
    return db_photo

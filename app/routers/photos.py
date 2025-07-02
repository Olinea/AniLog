from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.models.user import User
from app.models.animal import Animal
from app.models.photo import Photo
from app.schemas.photo import PhotoCreate, PhotoUpdate, Photo as PhotoSchema
from app.routers.auth import get_current_user, get_required_user

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

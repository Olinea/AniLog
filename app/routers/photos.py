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

# 示例代码，明天改
# 权限检查函数
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


@router.get("/", response_model=List[PhotoSchema])
async def read_photos(
    animal_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user)
):
    """获取动物图片列表"""

    query = db.query(Photo)
    if animal_id is not None:
        query = query.filter(Photo.animal_id == animal_id)

    photos = query.offset(skip).limit(limit).all()
    return photos


@router.get("/{photo_url}", response_model=PhotoSchema)
async def read_photo(
    photo_url: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user)
):
    """获取指定动物图片"""

    db_photo = db.query(Photo).filter(Photo.id == photo_url).first()
    if db_photo is None:
        raise HTTPException(status_code=404, detail="图片不存在")
    return db_photo


@router.put("/{photo_url}", response_model=PhotoSchema)
async def update_photo(
    photo_url: int,
    photo_update: PhotoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user)
):
    """更新动物图片 (上传者或管理员权限)"""

    db_photo = db.query(Photo).filter(Photo.id == photo_url).first()
    if db_photo is None:
        raise HTTPException(status_code=404, detail="图片不存在")

    # 检查权限：是上传者本人 或 manager >= 3
    is_uploader = bool(db_photo.user_id == current_user.id)
    manager_value = getattr(current_user, "manager", None)
    is_manager = (manager_value is not None and manager_value >= 3)

    # 如果尝试更新 verified 或 best 字段，必须是 manager >= 3
    update_data = photo_update.dict(exclude_unset=True)
    if ('verified' in update_data or 'best' in update_data) and not is_manager:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，只有管理员可以修改验证和最佳状态",
        )

    if not is_manager and not is_uploader:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，只有上传者或管理员可以修改图片信息",
        )

    # 检查关联的动物是否存在 (如果 animal_id 被更新)
    if 'animal_id' in update_data and update_data['animal_id'] != db_photo.animal_id:
        animal = db.query(Animal).filter(
            Animal.id == update_data['animal_id']).first()
        if animal is None:
            raise HTTPException(status_code=404, detail="关联的动物不存在")

    # 检查 photo_url 是否已存在 (如果 photo_url 被更新)
    if 'photo_url' in update_data and update_data['photo_url'] != db_photo.photo_url:
        existing_photo = db.query(Photo).filter(
            Photo.photo_url == update_data['photo_url']).first()
        if existing_photo:
            raise HTTPException(status_code=400, detail="图片ID已存在")

    for key, value in update_data.items():
        setattr(db_photo, key, value)

    db.commit()
    db.refresh(db_photo)
    return db_photo


@router.delete("/{photo_url}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_photo(
    photo_url: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user)
):
    """删除动物图片 (上传者或管理员权限)"""

    db_photo = db.query(Photo).filter(Photo.id == photo_url).first()
    if db_photo is None:
        raise HTTPException(status_code=404, detail="图片不存在")

    # 检查权限：是上传者本人 或 manager >= 3
    is_uploader = bool(db_photo.user_id == current_user.id)
    manager_value = getattr(current_user, "manager", None)
    is_manager = (manager_value is not None and manager_value >= 3)

    if not is_uploader and not is_manager:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，只有上传者或管理员可以删除图片",
        )

    db.delete(db_photo)
    db.commit()
    return None

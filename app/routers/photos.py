from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.models.user import User
from app.models.cat import Cat # 需要导入 Cat 模型来检查 cat_id 是否存在
from app.models.photo import Photo
from app.schemas.photo import PhotoCreate, PhotoUpdate, Photo as PhotoSchema
from app.routers.auth import get_current_user # 导入获取当前用户的依赖

router = APIRouter(
    prefix="/photos", # 添加前缀
    tags=["photos"] # 添加标签
)

# 权限检查函数 (与 cats 路由器中的类似，可以考虑提取到 utils)
def check_manager_permission(current_user: User = Depends(get_current_user)):
    """检查当前用户是否有 manager >= 3 的权限"""
    if current_user is None:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未认证",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if current_user.manager is None or current_user.manager < 3:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限",
        )
    return current_user

@router.post("/", response_model=PhotoSchema, status_code=status.HTTP_201_CREATED)
async def create_photo(
    photo: PhotoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # 任何认证用户都可以上传图片
):
    """上传新猫图片"""
    if current_user is None:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未认证",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 检查关联的猫是否存在
    cat = db.query(Cat).filter(Cat.id == photo.cat_id).first()
    if cat is None:
        raise HTTPException(status_code=404, detail="关联的猫不存在")

    # 检查 photo_id 是否已存在 (假设 photo_id 在外部系统中是唯一的)
    existing_photo = db.query(Photo).filter(Photo.photo_id == photo.photo_id).first()
    if existing_photo:
        raise HTTPException(status_code=400, detail="图片ID已存在")

    db_photo = Photo(
        **photo.dict(exclude={'verified', 'best'}), # 排除 verified 和 best，使用默认值
        user_id=current_user.id
    )

    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)
    return db_photo

@router.get("/", response_model=List[PhotoSchema])
async def read_photos(
    cat_id: Optional[int] = None, # 可选按猫过滤
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # 任何认证用户都可以读取列表
):
    """获取猫图片列表"""
    if current_user is None:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未认证",
            headers={"WWW-Authenticate": "Bearer"},
        )

    query = db.query(Photo)
    if cat_id is not None:
        query = query.filter(Photo.cat_id == cat_id)

    photos = query.offset(skip).limit(limit).all()
    return photos

@router.get("/{photo_id}", response_model=PhotoSchema)
async def read_photo(
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # 任何认证用户都可以读取单个
):
    """获取指定猫图片"""
    if current_user is None:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未认证",
            headers={"WWW-Authenticate": "Bearer"},
        )
    db_photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if db_photo is None:
        raise HTTPException(status_code=404, detail="图片不存在")
    return db_photo

@router.put("/{photo_id}", response_model=PhotoSchema)
async def update_photo(
    photo_id: int,
    photo_update: PhotoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # 允许上传者或管理员更新
):
    """更新猫图片 (上传者或管理员权限)"""
    if current_user is None:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未认证",
            headers={"WWW-Authenticate": "Bearer"},
        )

    db_photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if db_photo is None:
        raise HTTPException(status_code=404, detail="图片不存在")

    # 检查权限：是上传者本人 或 manager >= 3
    is_uploader = db_photo.user_id == current_user.id
    is_manager = current_user.manager is not None and current_user.manager >= 3

    # 如果尝试更新 verified 或 best 字段，必须是 manager >= 3
    update_data = photo_update.dict(exclude_unset=True)
    if ('verified' in update_data or 'best' in update_data) and not is_manager:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，只有管理员可以修改验证和最佳状态",
        )

    # 如果不是管理员，且尝试修改其他字段，必须是上传者本人
    # 注意：这里简化处理，如果不是管理员，只允许上传者修改非 verified/best 字段
    # 更精细的权限控制可能需要区分哪些字段可以被上传者修改
    if not is_manager and not is_uploader:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，只有上传者或管理员可以修改图片信息",
        )

    # 检查关联的猫是否存在 (如果 cat_id 被更新)
    if 'cat_id' in update_data and update_data['cat_id'] != db_photo.cat_id:
         cat = db.query(Cat).filter(Cat.id == update_data['cat_id']).first()
         if cat is None:
            raise HTTPException(status_code=404, detail="关联的猫不存在")

    # 检查 photo_id 是否已存在 (如果 photo_id 被更新)
    if 'photo_id' in update_data and update_data['photo_id'] != db_photo.photo_id:
        existing_photo = db.query(Photo).filter(Photo.photo_id == update_data['photo_id']).first()
        if existing_photo:
            raise HTTPException(status_code=400, detail="图片ID已存在")


    for key, value in update_data.items():
        setattr(db_photo, key, value)

    db.commit()
    db.refresh(db_photo)
    return db_photo

@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_photo(
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # 允许上传者或管理员删除
):
    """删除猫图片 (上传者或管理员权限)"""
    if current_user is None:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未认证",
            headers={"WWW-Authenticate": "Bearer"},
        )

    db_photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if db_photo is None:
        raise HTTPException(status_code=404, detail="图片不存在")

    # 检查权限：是上传者本人 或 manager >= 3
    is_uploader = db_photo.user_id == current_user.id
    is_manager = current_user.manager is not None and current_user.manager >= 3

    if not is_uploader and not is_manager:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，只有上传者或管理员可以删除图片",
        )

    db.delete(db_photo)
    db.commit()
    return None # 204 No Content 不需要返回内容

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.user import User
from app.models.cat import Cat
from app.schemas.cat import CatCreate, Cat as CatSchema
from app.routers.auth import get_current_user, get_required_user # 导入 get_required_user

router = APIRouter()

# 权限检查函数
def check_manager_permission(current_user: User = Depends(get_required_user)): # 依赖 get_required_user
    """检查当前用户是否有 manager >= 3 的权限"""
    # get_required_user 已经确保 current_user 不是 None
    manager_value = getattr(current_user, "manager", None)
    if manager_value is None or int(manager_value) < 3:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限",
        )
    return current_user

@router.post("/", response_model=CatSchema, status_code=status.HTTP_201_CREATED)
async def create_cat(
    cat: CatCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_manager_permission) # 依赖 check_manager_permission
):
    """创建新猫 (需要管理员权限)"""
    # 检查猫名是否已存在
    db_cat = db.query(Cat).filter(Cat.name == cat.name).first()
    if db_cat:
        raise HTTPException(status_code=400, detail="猫名已被使用")

    db_cat = Cat(**cat.dict())
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat

@router.get("/", response_model=List[CatSchema])
async def read_cats(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user) # 依赖 get_required_user
):
    """获取猫列表"""
    # get_required_user 已经确保认证
    cats = db.query(Cat).offset(skip).limit(limit).all()
    return cats

@router.get("/{cat_id}", response_model=CatSchema)
async def read_cat(
    cat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user) # 依赖 get_required_user
):
    """获取指定猫"""
    # get_required_user 已经确保认证
    db_cat = db.query(Cat).filter(Cat.id == cat_id).first()
    if db_cat is None:
        raise HTTPException(status_code=404, detail="猫不存在")
    return db_cat

@router.put("/{cat_id}", response_model=CatSchema)
async def update_cat(
    cat_id: int,
    cat: CatCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_manager_permission) # 依赖 check_manager_permission
):
    """更新猫 (需要管理员权限)"""
    db_cat = db.query(Cat).filter(Cat.id == cat_id).first()
    if db_cat is None:
        raise HTTPException(status_code=404, detail="猫不存在")

    # 检查更新后的猫名是否与现有其他猫冲突
    if cat.name != db_cat.name:
        existing_cat = db.query(Cat).filter(Cat.name == cat.name).first()
        if existing_cat:
             raise HTTPException(status_code=400, detail="猫名已被使用")

    for key, value in cat.dict(exclude_unset=True).items():
        setattr(db_cat, key, value)

    db.commit()
    db.refresh(db_cat)
    return db_cat

@router.delete("/{cat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cat(
    cat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_manager_permission) # 依赖 check_manager_permission
):
    """删除猫 (需要管理员权限)"""
    db_cat = db.query(Cat).filter(Cat.id == cat_id).first()
    if db_cat is None:
        raise HTTPException(status_code=404, detail="猫不存在")

    db.delete(db_cat)
    db.commit()
    return None
    db.delete(db_cat)
    db.commit()
    return None

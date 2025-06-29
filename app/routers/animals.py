from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.user import User
from app.models.animal import Animal
from app.schemas.animal import AnimalCreate, Animal as AnimalSchema
from app.routers.auth import get_current_user, get_required_user

router = APIRouter()

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

@router.post("/", response_model=AnimalSchema, status_code=status.HTTP_201_CREATED)
async def create_animal(
    animal: AnimalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_manager_permission)
):
    """创建新动物 (需要管理员权限)"""
    # 检查动物名是否已存在
    db_animal = db.query(Animal).filter(Animal.name == animal.name).first()
    if db_animal:
        raise HTTPException(status_code=400, detail="动物名已被使用")

    db_animal = Animal(**animal.dict())
    db.add(db_animal)
    db.commit()
    db.refresh(db_animal)
    return db_animal

@router.get("/", response_model=List[AnimalSchema])
async def read_animals(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user)
):
    """获取动物列表"""
    animals = db.query(Animal).offset(skip).limit(limit).all()
    return animals

@router.get("/{animal_id}", response_model=AnimalSchema)
async def read_animal(
    animal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user)
):
    """获取指定动物"""
    db_animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if db_animal is None:
        raise HTTPException(status_code=404, detail="动物不存在")
    return db_animal

@router.put("/{animal_id}", response_model=AnimalSchema)
async def update_animal(
    animal_id: int,
    animal: AnimalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_manager_permission)
):
    """更新动物 (需要管理员权限)"""
    db_animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if db_animal is None:
        raise HTTPException(status_code=404, detail="动物不存在")

    # 检查更新后的动物名是否与现有其他动物冲突
    if animal.name != db_animal.name:
        existing_animal = db.query(Animal).filter(Animal.name == animal.name).first()
        if existing_animal:
             raise HTTPException(status_code=400, detail="动物名已被使用")

    for key, value in animal.dict(exclude_unset=True).items():
        setattr(db_animal, key, value)

    db.commit()
    db.refresh(db_animal)
    return db_animal

@router.delete("/{animal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_animal(
    animal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_manager_permission)
):
    """删除动物 (需要管理员权限)"""
    db_animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if db_animal is None:
        raise HTTPException(status_code=404, detail="动物不存在")

    db.delete(db_animal)
    db.commit()
    return None

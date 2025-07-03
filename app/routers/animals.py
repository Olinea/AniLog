from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from typing import List

from app.db.database import get_db
from app.models.user import User
from app.models.animal import Animal
from app.models.photo import Photo
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
    
    # 新创建的动物没有照片，best_photo为None
    animal_data = AnimalSchema.from_orm(db_animal)
    animal_data.best_photo = None
    
    return animal_data

@router.get("/", response_model=List[AnimalSchema])
async def read_animals(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user)
):
    """获取动物列表"""
    # 使用左连接获取动物和其最佳照片
    animals_with_photos = db.query(Animal, Photo).outerjoin(
        Photo, and_(Animal.id == Photo.animal_id, Photo.best == True)
    ).offset(skip).limit(limit).all()
    
    result = []
    for animal, best_photo in animals_with_photos:
        animal_data = AnimalSchema.from_orm(animal)
        animal_data.best_photo = best_photo
        result.append(animal_data)
    
    return result

@router.get("/{animal_id}", response_model=AnimalSchema)
async def read_animal(
    animal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user)
):
    """获取指定动物"""
    # 使用左连接获取动物和其最佳照片
    result = db.query(Animal, Photo).outerjoin(
        Photo, and_(Animal.id == Photo.animal_id, Photo.best == True)
    ).filter(Animal.id == animal_id).first()
    
    if result is None:
        raise HTTPException(status_code=404, detail="动物不存在")
    
    animal, best_photo = result
    animal_data = AnimalSchema.from_orm(animal)
    animal_data.best_photo = best_photo
    
    return animal_data

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
    
    # 获取最佳照片
    best_photo = db.query(Photo).filter(
        Photo.animal_id == animal_id, 
        Photo.best == True
    ).first()
    
    animal_data = AnimalSchema.from_orm(db_animal)
    animal_data.best_photo = best_photo
    
    return animal_data

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

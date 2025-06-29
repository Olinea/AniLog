from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.user import User
from app.models.item import Item
from app.schemas.item import ItemCreate, Item as ItemSchema
from app.routers.auth import get_current_user, get_required_user # 导入 get_required_user

router = APIRouter()

@router.post("/", response_model=ItemSchema, status_code=status.HTTP_201_CREATED)
async def create_item(
    item: ItemCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user) # 依赖 get_required_user
):
    """创建新项目"""
    db_item = Item(**item.dict(), owner_id=current_user.id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/", response_model=List[ItemSchema])
async def read_items(
    skip: int = 0, 
    limit: int = 10, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user) # 依赖 get_required_user
):
    """获取项目列表"""
    items = db.query(Item).filter(Item.owner_id == current_user.id).offset(skip).limit(limit).all()
    return items

@router.get("/{item_id}", response_model=ItemSchema)
async def read_item(
    item_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user) # 依赖 get_required_user
):
    """获取指定项目"""
    db_item = db.query(Item).filter(Item.id == item_id, Item.owner_id == current_user.id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="项目不存在或无权访问")
    return db_item

@router.put("/{item_id}", response_model=ItemSchema)
async def update_item(
    item_id: int, 
    item: ItemCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user) # 依赖 get_required_user
):
    """更新项目"""
    db_item = db.query(Item).filter(Item.id == item_id, Item.owner_id == current_user.id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="项目不存在或无权访问")
    
    for key, value in item.dict().items():
        setattr(db_item, key, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user) # 依赖 get_required_user
):
    """删除项目"""
    db_item = db.query(Item).filter(Item.id == item_id, Item.owner_id == current_user.id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="项目不存在或无权访问")
    
    db.delete(db_item)
    db.commit()
    return None

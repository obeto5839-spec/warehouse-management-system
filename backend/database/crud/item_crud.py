from sqlalchemy.orm import Session
from database.models.item_model import Item, ItemStatus
from database.schemas.item_schema import ItemCreate, ItemUpdate
from typing import Optional

def create_item(db: Session, item: ItemCreate):
    db_item = Item(
        item_sn=item.item_sn,
        sku_id=item.sku_id,
        grade=item.grade,
        factory_sn=item.factory_sn,
        cost_price=item.cost_price,
        location_id=item.location_id,
        status=ItemStatus.PENDING_SHELVING # 默认为待上架
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_item(db: Session, item_sn: str):
    return db.query(Item).filter(Item.item_sn == item_sn).first()

def get_items(db: Session, skip: int = 0, limit: int = 100, sku_id: Optional[int] = None):
    query = db.query(Item)
    if sku_id:
        query = query.filter(Item.sku_id == sku_id)
    return query.offset(skip).limit(limit).all()

def update_item(db: Session, item_sn: str, item_update: ItemUpdate):
    db_item = get_item(db, item_sn)
    if not db_item:
        return None
    
    update_data = item_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
        
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_item(db: Session, item_sn: str):
    db_item = get_item(db, item_sn)
    if db_item:
        db.delete(db_item)
        db.commit()
    return db_item

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
        machine_sn=item.machine_sn,
        location_id=item.location_id,
        status=ItemStatus.PENDING_SHELVING
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


def get_items_by_machine_sn(db: Session, machine_sn: str):
    """根据整机编码获取所有绑定的配件"""
    return db.query(Item).filter(Item.machine_sn == machine_sn).all()


def get_active_items_by_machine_sn(db: Session, machine_sn: str):
    """获取整机中还未售出的配件"""
    return db.query(Item).filter(
        Item.machine_sn == machine_sn,
        Item.status != "sold"
    ).all()


def unbind_machine(db: Session, item_sn: str):
    """将配件从整机中解绑（剪断绳子）"""
    db_item = get_item(db, item_sn)
    if db_item:
        db_item.machine_sn = None
        db.commit()
        db.refresh(db_item)
    return db_item


def batch_update_machine_status(db: Session, machine_sn: str, status):
    """批量更新整机所有配件的状态"""
    items = get_active_items_by_machine_sn(db, machine_sn)
    for item in items:
        item.status = status
        item.location_id = None if status == "sold" else item.location_id
    db.commit()
    return items

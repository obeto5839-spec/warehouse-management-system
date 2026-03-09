from sqlalchemy.orm import Session
from sqlalchemy import desc
from database.models.order_model import Order
from database.schemas.order_schema import OrderCreate, OrderUpdate
from typing import Optional


def create_order(db: Session, order_in: OrderCreate):
    db_order = Order(**order_in.model_dump())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


def get_order(db: Session, order_id: int):
    return db.query(Order).filter(Order.id == order_id).first()


def get_orders(db: Session, skip: int = 0, limit: int = 50,
               order_status: Optional[str] = None,
               platform: Optional[str] = None,
               customer_id: Optional[str] = None,
               order_type: Optional[str] = None):
    query = db.query(Order)
    if order_status:
        query = query.filter(Order.order_status == order_status)
    if platform:
        query = query.filter(Order.platform == platform)
    if customer_id:
        query = query.filter(Order.customer_id.ilike(f"%{customer_id}%"))
    if order_type:
        query = query.filter(Order.order_type == order_type)
    return query.order_by(desc(Order.created_at)).offset(skip).limit(limit).all()


def count_orders(db: Session,
                 order_status: Optional[str] = None,
                 platform: Optional[str] = None,
                 customer_id: Optional[str] = None,
                 order_type: Optional[str] = None) -> int:
    """统计符合条件的订单总数"""
    from sqlalchemy import func
    query = db.query(func.count(Order.id))
    if order_status:
        query = query.filter(Order.order_status == order_status)
    if platform:
        query = query.filter(Order.platform == platform)
    if customer_id:
        query = query.filter(Order.customer_id.ilike(f"%{customer_id}%"))
    if order_type:
        query = query.filter(Order.order_type == order_type)
    return query.scalar() or 0


def update_order(db: Session, order_id: int, order_update: OrderUpdate):
    db_order = get_order(db, order_id)
    if not db_order:
        return None
    update_data = order_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_order, key, value)
    db.commit()
    db.refresh(db_order)
    return db_order


def delete_order(db: Session, order_id: int):
    db_order = get_order(db, order_id)
    if db_order:
        db.delete(db_order)
        db.commit()
    return db_order


def count_orders_by_status(db: Session):
    """统计各状态的订单数量"""
    from sqlalchemy import func
    results = db.query(Order.order_status, func.count(Order.id)).group_by(Order.order_status).all()
    return {status: count for status, count in results}

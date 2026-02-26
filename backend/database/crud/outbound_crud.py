from sqlalchemy.orm import Session
from database.models.outbound_model import OutboundRecord
from database.schemas.outbound_schema import OutboundRecordCreate, OutboundRecordUpdate
from typing import Optional

def create_outbound_record(db: Session, record: OutboundRecordCreate):
    db_record = OutboundRecord(
        order_no=record.order_no,
        item_sn=record.item_sn,
        sell_price=record.sell_price,
        buyer_info=record.buyer_info
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

def get_outbound_record(db: Session, record_id: int):
    return db.query(OutboundRecord).filter(OutboundRecord.id == record_id).first()

def get_outbound_records(db: Session, skip: int = 0, limit: int = 100, order_no: Optional[str] = None, item_sn: Optional[str] = None):
    query = db.query(OutboundRecord)
    if order_no:
        query = query.filter(OutboundRecord.order_no == order_no)
    if item_sn:
        query = query.filter(OutboundRecord.item_sn == item_sn)
    return query.order_by(OutboundRecord.outbound_time.desc()).offset(skip).limit(limit).all()

def update_outbound_record(db: Session, record_id: int, record_update: OutboundRecordUpdate):
    db_record = get_outbound_record(db, record_id)
    if not db_record:
        return None
    
    update_data = record_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_record, key, value)
        
    db.commit()
    db.refresh(db_record)
    return db_record

def delete_outbound_record(db: Session, record_id: int):
    db_record = get_outbound_record(db, record_id)
    if db_record:
        db.delete(db_record)
        db.commit()
    return db_record

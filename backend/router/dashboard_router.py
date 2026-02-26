from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date

from database.schemas.app_result import AppResult
from database.database import get_db
from database.models.sku_model import SKU
from database.models.item_model import Item
from database.schemas.item_schema import ItemStatus
from database.models.location_model import Location
from database.models.outbound_model import OutboundRecord

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
    responses={404: {"description": "Not found"}},
)


@router.get("/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """首页统计数据"""
    sku_count = db.query(func.count(SKU.id)).scalar()
    in_stock_count = db.query(func.count(Item.item_sn)).filter(Item.status == "in_stock").scalar()
    location_count = db.query(func.count(Location.id)).scalar()

    today_start = datetime.combine(date.today(), datetime.min.time())
    today_outbound = db.query(func.count(OutboundRecord.id)).filter(
        OutboundRecord.outbound_time >= today_start
    ).scalar()

    return AppResult(code=200, message="success", data={
        "sku_count": sku_count,
        "in_stock_count": in_stock_count,
        "location_count": location_count,
        "today_outbound": today_outbound,
    })

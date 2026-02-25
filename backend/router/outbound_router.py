# backend/app/router/outbound_router.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

# 导入你的统一返回模型和依赖
from database.schemas.app_result import AppResult
from database.schemas.outbound_schema import OutboundRecordCreate  # 之前写好的出库Schema
from database.database import get_db
from service.outbound_service import OutboundService
from utils.log_manage import init_logger

logging = init_logger()

router = APIRouter(
    prefix="/outbound",
    tags=["Orders & Shipping"],
    responses={404: {"description": "Not found"}},
)

@router.post("/ship")
async def create_shipping_order(query: OutboundRecordCreate, db: Session = Depends(get_db)):
    """
    扫码出货：记录交易价格，物品状态改为'已出库'，清空库位
    """
    logging.info(f"执行出库发货, 订单号: {query.order_no}, 物品: {query.item_sn}")
    
    service = OutboundService(db)
    result = await service.execute_shipping(query)
    
    # 如果内部抛出异常或者返回特定格式，可以做相应判断
    if not result:
        return AppResult(code=400, message="发货失败，可能物品不存在或状态不对", data=None)
        
    return AppResult(code=200, message="发货成功", data=result)

@router.get("/detail/{order_no}")
async def get_order_detail(order_no: str, db: Session = Depends(get_db)):
    """
    查询发货单详情 (算利润、看买家信息)
    """
    service = OutboundService(db)
    result = await service.get_order_detail(order_no)
    
    if not result:
        return AppResult(code=404, message="订单不存在", data=None)
        
    return AppResult(code=200, message="success", data=result)
    
@router.get("/list")
async def get_outbound_list(
    item_sn: Optional[str] = None, 
    skip: int = 0, 
    limit: int = 10, 
    db: Session = Depends(get_db)
):
    """
    出货明细列表查询
    """
    service = OutboundService(db)
    results = await service.get_outbound_list(item_sn, skip, limit)
    return AppResult(code=200, message="success", data=results)
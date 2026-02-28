from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from database.schemas.app_result import AppResult
from database.schemas.order_schema import OrderCreate, OrderUpdate
from database.database import get_db
from service.order_service import OrderService
from utils.log_manage import init_logger

logging = init_logger()

router = APIRouter(
    prefix="/orders",
    tags=["交易订单"],
    responses={404: {"description": "Not found"}},
)


@router.post("/create")
async def create_order(data: OrderCreate, db: Session = Depends(get_db)):
    logging.info(f"新建订单, 平台: {data.platform}, 客户: {data.customer_id}")
    service = OrderService(db)
    result = await service.create(data)
    return AppResult(code=200, message="订单创建成功", data=result)


@router.get("/list")
async def list_orders(
    skip: int = Query(0),
    limit: int = Query(50),
    order_status: Optional[str] = Query(None, description="按状态筛选"),
    platform: Optional[str] = Query(None, description="按平台筛选"),
    db: Session = Depends(get_db)
):
    service = OrderService(db)
    result = await service.list(skip, limit, order_status, platform)
    return AppResult(code=200, message="success", data=result)


@router.get("/stats")
async def order_stats(db: Session = Depends(get_db)):
    service = OrderService(db)
    result = await service.stats()
    return AppResult(code=200, message="success", data=result)


@router.get("/{order_id}")
async def get_order(order_id: int, db: Session = Depends(get_db)):
    service = OrderService(db)
    result = await service.get(order_id)
    if not result:
        return AppResult(code=404, message="订单不存在", data=None)
    return AppResult(code=200, message="success", data=result)


@router.put("/{order_id}")
async def update_order(order_id: int, data: OrderUpdate, db: Session = Depends(get_db)):
    logging.info(f"更新订单 #{order_id}")
    service = OrderService(db)
    result = await service.update(order_id, data)
    if isinstance(result, dict) and "error" in result:
        return AppResult(code=404, message=result["error"], data=None)
    return AppResult(code=200, message="更新成功", data=result)


@router.delete("/{order_id}")
async def delete_order(order_id: int, db: Session = Depends(get_db)):
    logging.info(f"删除订单 #{order_id}")
    service = OrderService(db)
    result = await service.delete(order_id)
    if isinstance(result, dict) and "error" in result:
        return AppResult(code=404, message=result["error"], data=None)
    return AppResult(code=200, message="删除成功", data=None)

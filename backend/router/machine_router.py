from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal

from database.schemas.app_result import AppResult
from database.database import get_db
from service.machine_service import MachineService
from utils.log_manage import init_logger

logging = init_logger()

router = APIRouter(
    prefix="/machine",
    tags=["Machine (整机管理)"],
    responses={404: {"description": "Not found"}},
)


class MachineShipRequest(BaseModel):
    machine_sn: str = Field(..., description="整机编码")
    order_no: str = Field(..., description="订单号")
    sell_price: Decimal = Field(..., description="整机售价")
    buyer_info: Optional[str] = Field(None, description="买家信息")


class UnbindSellRequest(BaseModel):
    item_sn: str = Field(..., description="配件编码")
    order_no: str = Field(..., description="订单号")
    sell_price: Decimal = Field(..., description="售价")
    buyer_info: Optional[str] = Field(None, description="买家信息")


@router.get("/items/{machine_sn}")
async def get_machine_items(machine_sn: str, db: Session = Depends(get_db)):
    """
    查询整机下所有配件
    扫整机码 → 列出所有绑定的配件及状态
    """
    logging.info(f"查询整机配件, machine_sn: {machine_sn}")

    service = MachineService(db)
    result = await service.get_machine_items(machine_sn)

    if isinstance(result, dict) and "error" in result:
        logging.warning(f"查询整机失败: {result['error']}")
        return AppResult(code=404, message=result["error"], data=None)
    return AppResult(code=200, message="success", data=result)


@router.post("/ship")
async def ship_machine(query: MachineShipRequest, db: Session = Depends(get_db)):
    """
    整机一键出库
    扫整机码 → 所有配件批量标记已售 → 生成出库记录
    """
    logging.info(f"整机出库, machine_sn: {query.machine_sn}, order_no: {query.order_no}")

    service = MachineService(db)
    result = await service.ship_machine(
        query.machine_sn, query.order_no, query.sell_price, query.buyer_info
    )

    if isinstance(result, dict) and "error" in result:
        logging.warning(f"整机出库失败: {result['error']}")
        return AppResult(code=400, message=result["error"], data=None)

    logging.info(f"整机出库成功, machine_sn: {query.machine_sn}, 配件数: {result['item_count']}, 利润: {result['profit']}")
    return AppResult(code=200, message="整机出库成功", data=result)


@router.post("/unbind-sell")
async def unbind_and_sell(query: UnbindSellRequest, db: Session = Depends(get_db)):
    """
    拆件出库
    从整机中拆出单个配件 → 解绑 → 单独出库
    """
    logging.info(f"拆件出库, item_sn: {query.item_sn}, order_no: {query.order_no}")

    service = MachineService(db)
    result = await service.unbind_and_sell(
        query.item_sn, query.order_no, query.sell_price, query.buyer_info
    )

    if isinstance(result, dict) and "error" in result:
        logging.warning(f"拆件出库失败: {result['error']}")
        return AppResult(code=400, message=result["error"], data=None)

    logging.info(f"拆件出库成功, item_sn: {query.item_sn}")
    return AppResult(code=200, message="拆件出库成功", data=result)


@router.get("/check/{item_sn}")
async def check_binding(item_sn: str, db: Session = Depends(get_db)):
    """
    检查配件是否属于某台整机
    出库前调用，如果属于整机会提示用户
    """
    service = MachineService(db)
    result = await service.check_machine_binding(item_sn)

    if isinstance(result, dict) and "error" in result:
        return AppResult(code=404, message=result["error"], data=None)
    return AppResult(code=200, message="success", data=result)

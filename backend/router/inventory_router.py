# backend/app/router/inventory_router.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

# 导入你的统一返回模型和依赖
from database.schemas.app_result import AppResult
from database.database import get_db
from service.inventory_service import InventoryService
from utils.log_manage import init_logger

logging = init_logger()

router = APIRouter(
    prefix="/inventory",
    tags=["Inventory Operations"],
    responses={404: {"description": "Not found"}},
)

# --- 定义接收扫码参数的请求模型 ---
class ShelveRequestModel(BaseModel):
    item_sn: str        # 扫配件上的二维码
    location_code: str  # 扫货架上的条码

class PickRequestModel(BaseModel):
    item_sn: str        # 扫配件条码进行拣货/下架

# --- 路由接口 ---
@router.post("/shelve")
async def shelve_item(query: ShelveRequestModel, db: Session = Depends(get_db)):
    """
    扫码上架：将物品绑定到对应库位，状态改为'在库'
    """
    logging.info(f"执行上架操作, 物品: {query.item_sn}, 目标库位: {query.location_code}")
    service = InventoryService(db)
    
    # 执行业务逻辑
    result = await service.shelve_item(query)
    return AppResult(code=200, message="上架成功", data=result)

@router.post("/pick")
async def pick_item(query: PickRequestModel, db: Session = Depends(get_db)):
    """
    扫码拣货：将物品从当前库位移出 (例如备货、准备复测等)
    """
    service = InventoryService(db)
    result = await service.pick_item(query)
    return AppResult(code=200, message="拣货成功", data=result)

@router.get("/location/{location_code}")
async def get_location_items(location_code: str, db: Session = Depends(get_db)):
    """
    盘点：查询指定库位上目前有哪些物品
    """
    service = InventoryService(db)
    result = await service.get_location_items(location_code)
    return AppResult(code=200, message="success", data=result)

@router.get("/list")
async def get_inventory_list(
    status: Optional[str] = None, 
    sku_id: Optional[int] = None, 
    skip: int = 0, 
    limit: int = 10, 
    db: Session = Depends(get_db)
):
    """
    全局库存查询 (支持按状态、SKU分页查询)
    """
    service = InventoryService(db)
    results = await service.get_inventory_list(status, sku_id, skip, limit)
    return AppResult(code=200, message="success", data=results)
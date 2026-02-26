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
    
    result = await service.shelve_item(query)
    
    if isinstance(result, dict) and "error" in result:
        logging.warning(f"上架失败: {result['error']}, 物品: {query.item_sn}")
        return AppResult(code=400, message=result["error"], data=None)
    
    logging.info(f"上架成功, 物品: {query.item_sn}, 库位: {query.location_code}")
    return AppResult(code=200, message="上架成功", data=result)

@router.post("/pick")
async def pick_item(query: PickRequestModel, db: Session = Depends(get_db)):
    """
    扫码拣货：将物品从当前库位移出 (例如备货、准备复测等)
    """
    logging.info(f"执行拣货操作, 物品: {query.item_sn}")
    service = InventoryService(db)
    result = await service.pick_item(query)
    
    if isinstance(result, dict) and "error" in result:
        logging.warning(f"拣货失败: {result['error']}, 物品: {query.item_sn}")
        return AppResult(code=400, message=result["error"], data=None)
    
    logging.info(f"拣货成功, 物品: {query.item_sn}")
    return AppResult(code=200, message="拣货成功", data=result)

@router.get("/location/{location_code}")
async def get_location_items(location_code: str, db: Session = Depends(get_db)):
    """
    盘点：查询指定库位上目前有哪些物品
    """
    logging.info(f"查询库位物品, 库位: {location_code}")
    service = InventoryService(db)
    result = await service.get_location_items(location_code)
    
    if isinstance(result, dict) and "error" in result:
        logging.warning(f"查询库位失败: {result['error']}, 库位: {location_code}")
        return AppResult(code=400, message=result["error"], data=None)
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
    logging.info(f"查询库存列表, status: {status}, sku_id: {sku_id}, skip: {skip}, limit: {limit}")
    service = InventoryService(db)
    results = await service.get_inventory_list(status, sku_id, skip, limit)
    return AppResult(code=200, message="success", data=results)
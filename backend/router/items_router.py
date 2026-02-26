# backend/app/router/
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from database.schemas.app_result import AppResult
from database.schemas.item_schema import ItemCreate
from service.items_service import ItemService
from database.database import get_db # SQLAlchemy 获取 session 的方法
from utils.log_manage import init_logger

logging = init_logger()

router = APIRouter(
    prefix="/items",
    tags=["Items Management"],
    # dependencies=[Depends(get_token_header)], # 如果你需要鉴权可以随时开启
    responses={404: {"description": "Not found"}},
)

@router.post("/create")
async def create_item(query: ItemCreate, db: Session = Depends(get_db)):
    """
    录入新配件 (贴码)
    """
    logging.info(f"开始录入配件, item_sn: {query.item_sn}, sku_id: {query.sku_id}")
    
    service = ItemService(db)
    result = await service.create_item_profile(query)
    
    # 检查业务错误
    if isinstance(result, dict) and "error" in result:
        logging.warning(f"录入配件失败: {result['error']}")
        return AppResult(code=400, message=result["error"], data=None)
    
    logging.info(f"录入配件成功, item_sn: {query.item_sn}")
    return AppResult(code=200, message="录入成功", data=result)

@router.get("/detail/{item_sn}")
async def get_item_detail(item_sn: str, db: Session = Depends(get_db)):
    """
    扫码查询配件档案
    """
    logging.info(f"查询配件详情, item_sn: {item_sn}")
    
    service = ItemService(db)
    result = await service.get_item_detail(item_sn)
    
    if not result:
        logging.warning(f"配件不存在, item_sn: {item_sn}")
        return AppResult(code=404, message="配件不存在", data=None)
        
    return AppResult(code=200, message="success", data=result)
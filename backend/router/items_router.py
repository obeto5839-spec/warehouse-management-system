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
    logging.info(f"开始录入配件, sku_id: {query.sku_id}")
    
    # 实例化 Service，注入 db
    service = ItemService(db)
    
    # 执行业务逻辑
    result = await service.create_item_profile(query)
    
    # 统一格式返回
    return AppResult(code=200, message="success", data=result)

@router.get("/detail/{item_sn}")
async def get_item_detail(item_sn: str, db: Session = Depends(get_db)):
    """
    扫码查询配件档案
    """
    service = ItemService(db)
    result = await service.get_item_detail(item_sn)
    
    if not result:
        return AppResult(code=404, message="item not found", data=None)
        
    return AppResult(code=200, message="success", data=result)
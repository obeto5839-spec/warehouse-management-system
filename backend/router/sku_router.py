from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

# 导入你的统一返回模型和依赖
from database.schemas.app_result import AppResult
from database.schemas.sku_schema import SKUCreate
from database.database import get_db
from service.skus_service import SKUService
from utils.log_manage import init_logger

logging = init_logger()

router = APIRouter(
    prefix="/skus",
    tags=["1. SKUs Management (标准库)"],
    responses={404: {"description": "Not found"}},
)

@router.post("/create")
async def create_sku(query: SKUCreate, db: Session = Depends(get_db)):
    """
    录入标准配件档案 (SKU)
    """
    service = SKUService(db)
    result = await service.create_sku(query)
    
    if not result:
        return AppResult(code=400, message="该型号已存在，请勿重复录入", data=None)
        
    return AppResult(code=200, message="标准件录入成功", data=result)

@router.get("/search")
async def search_skus(
    category: str = Query(..., description="配件分类，如：CPU、主板"),
    brand: Optional[str] = Query(None, description="品牌，如：Intel (可选)"),
    keyword: str = Query("", description="型号模糊搜索词，如输入 '12' 搜出 '12700'"),
    limit: int = Query(10, description="限制返回条数，保证前端下拉框不卡顿"),
    db: Session = Depends(get_db)
):
    """
    提供给前端下拉框使用的级联与模糊搜索接口
    """
    service = SKUService(db)
    # 注意：这里调用的是 search_skus，需要在 service 中实现
    results = await service.search_skus(category=category, brand=brand, keyword=keyword, limit=limit)
    
    return AppResult(code=200, message="success", data=results)
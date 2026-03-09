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
    logging.info(f"录入SKU, category: {query.category}, brand: {query.brand}, model: {query.model_name}")
    
    service = SKUService(db)
    result = await service.create_sku(query)
    
    if not result:
        logging.warning(f"SKU已存在, category: {query.category}, brand: {query.brand}, model: {query.model_name}")
        return AppResult(code=400, message="该型号已存在，请勿重复录入", data=None)
    
    logging.info(f"SKU录入成功, id: {result.get('id')}")
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
    logging.info(f"搜索SKU, category: {category}, brand: {brand}, keyword: {keyword}")
    
    service = SKUService(db)
    results = await service.search_skus(category=category, brand=brand, keyword=keyword, limit=limit)
    
    return AppResult(code=200, message="success", data=results)


@router.get("/autocomplete")
async def autocomplete_skus(
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    limit: int = Query(10, description="返回条数"),
    db: Session = Depends(get_db)
):
    """
    全局模糊搜索 SKU（配件录入时自动补全用）
    输入关键词 → 在分类/品牌/型号中匹配 → 返回匹配的 SKU 列表
    """
    from database.crud.sku_crud import fuzzy_search_skus
    skus = fuzzy_search_skus(db, keyword, limit)
    result = [{
        "id": s.id,
        "category": s.category,
        "brand": s.brand,
        "series": s.series,
        "model_name": s.model_name,
        "label": f"{s.category} / {s.brand} / {(s.series + ' ') if s.series else ''}{s.model_name}",
    } for s in skus]
    return AppResult(code=200, message="success", data=result)


@router.get("/property-schema")
async def get_property_schema(
    category: Optional[str] = Query(None, description="分类名，不传则返回全部分类的属性定义")
):
    """
    获取各分类的规格参数字段定义（前端动态渲染表单用）
    返回：{ "显卡": [{key, label, placeholder, required, type, options}, ...], ... }
    """
    from utils.sku_validator import get_property_schema as _get
    schema = _get(category)
    return AppResult(code=200, message="success", data=schema)


@router.get("/models")
async def get_models(
    category: str = Query(..., description="分类名"),
    brand: str = Query(..., description="品牌名"),
    db: Session = Depends(get_db)
):
    """获取某分类+品牌下的型号列表（含 properties，选型号后自动回填规格）"""
    from database.crud.sku_crud import get_models_by_category_brand
    skus = get_models_by_category_brand(db, category, brand)
    result = [{
        "id": s.id,
        "series": s.series,
        "model_name": s.model_name,
        "properties": s.properties or {},
    } for s in skus]
    return AppResult(code=200, message="success", data=result)


@router.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    """获取所有分类列表（下拉框用）"""
    from database.crud.sku_crud import get_distinct_categories
    categories = get_distinct_categories(db)
    return AppResult(code=200, message="success", data=categories)


@router.get("/brands")
async def get_brands(
    category: str = Query(..., description="分类名"),
    db: Session = Depends(get_db)
):
    """获取某分类下的品牌列表（级联下拉用）"""
    from database.crud.sku_crud import get_brands_by_category
    brands = get_brands_by_category(db, category)
    return AppResult(code=200, message="success", data=brands)
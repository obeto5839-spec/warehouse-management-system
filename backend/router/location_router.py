from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from database.schemas.app_result import AppResult
from database.schemas.location_schema import LocationCreate, LocationUpdate
from database.database import get_db
from service.location_service import LocationService
from utils.log_manage import init_logger

logging = init_logger()

router = APIRouter(
    prefix="/locations",
    tags=["Location Management (库位管理)"],
    responses={404: {"description": "Not found"}},
)


@router.post("/create")
async def create_location(query: LocationCreate, db: Session = Depends(get_db)):
    """
    创建库位
    """
    logging.info(f"创建库位, code: {query.location_code}, name: {query.location_name}")
    
    service = LocationService(db)
    result = await service.create_location(query)
    
    if isinstance(result, dict) and "error" in result:
        logging.warning(f"创建库位失败: {result['error']}")
        return AppResult(code=400, message=result["error"], data=None)
    
    logging.info(f"创建库位成功, id: {result.id}, code: {query.location_code}")
    return AppResult(code=200, message="创建成功", data=result)


@router.get("/list")
async def get_location_list(
    parent_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    获取库位列表
    - parent_id 为空时返回顶级库位
    - parent_id 有值时返回该库位下的子库位
    """
    logging.info(f"查询库位列表, parent_id: {parent_id}, skip: {skip}, limit: {limit}")
    
    service = LocationService(db)
    results = await service.get_location_list(parent_id=parent_id, skip=skip, limit=limit)
    return AppResult(code=200, message="success", data=results)


@router.get("/detail/{location_id}")
async def get_location_detail(location_id: int, db: Session = Depends(get_db)):
    """
    获取库位详情
    """
    logging.info(f"查询库位详情, id: {location_id}")
    
    service = LocationService(db)
    result = await service.get_location_detail(location_id)
    
    if not result:
        logging.warning(f"库位不存在, id: {location_id}")
        return AppResult(code=404, message="库位不存在", data=None)
    
    return AppResult(code=200, message="success", data=result)


@router.get("/code/{location_code}")
async def get_location_by_code(location_code: str, db: Session = Depends(get_db)):
    """
    根据编码获取库位
    """
    logging.info(f"查询库位, code: {location_code}")
    
    service = LocationService(db)
    result = await service.get_location_by_code(location_code)
    
    if not result:
        logging.warning(f"库位不存在, code: {location_code}")
        return AppResult(code=404, message="库位不存在", data=None)
    
    return AppResult(code=200, message="success", data=result)


@router.put("/update/{location_id}")
async def update_location(location_id: int, query: LocationUpdate, db: Session = Depends(get_db)):
    """
    更新库位信息
    """
    logging.info(f"更新库位, id: {location_id}")
    
    service = LocationService(db)
    result = await service.update_location(location_id, query)
    
    if isinstance(result, dict) and "error" in result:
        logging.warning(f"更新库位失败: {result['error']}")
        return AppResult(code=400, message=result["error"], data=None)
    
    logging.info(f"更新库位成功, id: {location_id}")
    return AppResult(code=200, message="更新成功", data=result)


@router.delete("/delete/{location_id}")
async def delete_location(location_id: int, db: Session = Depends(get_db)):
    """
    删除库位
    """
    logging.info(f"删除库位, id: {location_id}")
    
    service = LocationService(db)
    result = await service.delete_location(location_id)
    
    if isinstance(result, dict) and "error" in result:
        logging.warning(f"删除库位失败: {result['error']}")
        return AppResult(code=400, message=result["error"], data=None)
    
    logging.info(f"删除库位成功, id: {location_id}")
    return AppResult(code=200, message="删除成功", data=None)

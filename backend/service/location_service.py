from sqlalchemy.orm import Session
from database.crud.location_crud import (
    create_location, 
    get_location, 
    get_location_by_code, 
    get_locations,
    update_location,
    delete_location
)
from database.schemas.location_schema import LocationCreate, LocationUpdate, LocationResponse


class LocationService:
    def __init__(self, db: Session):
        self.db = db

    async def create_location(self, location_data: LocationCreate):
        """创建库位"""
        # 检查库位编码是否已存在
        existing = get_location_by_code(self.db, location_data.location_code)
        if existing:
            return {"error": f"库位编码 {location_data.location_code} 已存在"}
        
        # 如果指定了父级，检查父级是否存在
        if location_data.parent_id:
            parent = get_location(self.db, location_data.parent_id)
            if not parent:
                return {"error": "父级库位不存在"}
        
        db_location = create_location(self.db, location_data)
        return LocationResponse.model_validate(db_location)

    async def get_location_detail(self, location_id: int):
        """获取库位详情"""
        db_location = get_location(self.db, location_id)
        if not db_location:
            return None
        return LocationResponse.model_validate(db_location)

    async def get_location_by_code(self, location_code: str):
        """根据编码获取库位"""
        db_location = get_location_by_code(self.db, location_code)
        if not db_location:
            return None
        return LocationResponse.model_validate(db_location)

    async def get_location_list(self, parent_id: int = None, skip: int = 0, limit: int = 100):
        """获取库位列表"""
        db_locations = get_locations(self.db, skip=skip, limit=limit, parent_id=parent_id)
        return [LocationResponse.model_validate(loc) for loc in db_locations]

    async def update_location(self, location_id: int, location_data: LocationUpdate):
        """更新库位"""
        db_location = get_location(self.db, location_id)
        if not db_location:
            return {"error": "库位不存在"}
        
        # 如果要修改编码，检查新编码是否已存在
        if location_data.location_code:
            existing = get_location_by_code(self.db, location_data.location_code)
            if existing and existing.id != location_id:
                return {"error": f"库位编码 {location_data.location_code} 已被使用"}
        
        db_location = update_location(self.db, location_id, location_data)
        return LocationResponse.model_validate(db_location)

    async def delete_location(self, location_id: int):
        """删除库位"""
        db_location = get_location(self.db, location_id)
        if not db_location:
            return {"error": "库位不存在"}
        
        # 检查是否有子库位
        if db_location.children:
            return {"error": "该库位下有子库位，请先删除子库位"}
        
        # 检查是否有物品
        if db_location.items:
            return {"error": "该库位下有物品，请先移走物品"}
        
        delete_location(self.db, location_id)
        return {"message": "删除成功"}

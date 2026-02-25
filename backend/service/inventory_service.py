from sqlalchemy.orm import Session
from database.crud.item_crud import get_item, update_item, get_items
from database.crud.location_crud import get_location_by_code
from database.schemas.item_schema import ItemUpdate, ItemStatus

class InventoryService:
    def __init__(self, db: Session):
        self.db = db

    async def shelve_item(self, query):
        """上架"""
        # 1. 校验库位是否存在
        location = get_location_by_code(self.db, query.location_code)
        if not location:
            return {"error": "Invalid location code"}

        # 2. 校验物品是否存在
        item = get_item(self.db, query.item_sn)
        if not item:
            return {"error": "Item not found"}
            
        # 3. 更新物品状态和库位
        update_data = ItemUpdate(
            location_id=location.id,
            status=ItemStatus.IN_STOCK
        )
        return update_item(self.db, item.item_sn, update_data)

    async def pick_item(self, query):
        """拣货/下架"""
        item = get_item(self.db, query.item_sn)
        if not item:
            return {"error": "Item not found"}
            
        # 下架：清空库位，状态改为待上架(或其他中间状态)
        update_data = ItemUpdate(
            location_id=None,
            status=ItemStatus.PENDING_SHELVING 
        )
        return update_item(self.db, item.item_sn, update_data)

    async def get_location_items(self, location_code: str):
        """查询库位上的物品"""
        location = get_location_by_code(self.db, location_code)
        if not location:
            return {"error": "Invalid location code"}
        return location.items # 利用 ORM 关系直接获取

    async def get_inventory_list(self, status=None, sku_id=None, skip=0, limit=10):
        # 这里需要扩展 CRUD 支持更多筛选，目前仅演示
        return get_items(self.db, skip=skip, limit=limit, sku_id=sku_id)

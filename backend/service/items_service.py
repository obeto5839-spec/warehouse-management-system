from sqlalchemy.orm import Session
from database.crud.item_crud import create_item, get_item, get_active_items_by_machine_sn
from database.crud.sku_crud import get_sku
from database.crud.location_crud import get_location
from database.schemas.item_schema import ItemCreate, ItemResponse

class ItemService:
    def __init__(self, db: Session):
        self.db = db

    async def create_item_profile(self, item_data: ItemCreate):
        if get_item(self.db, item_data.item_sn):
            return {"error": f"Item SN {item_data.item_sn} already exists"}
        
        db_item = create_item(self.db, item_data)
        return ItemResponse.model_validate(db_item)

    async def get_item_detail(self, item_sn: str):
        db_item = get_item(self.db, item_sn)
        if not db_item:
            return None

        result = ItemResponse.model_validate(db_item).model_dump()

        # 补充 SKU 信息
        sku = get_sku(self.db, db_item.sku_id)
        if sku:
            result["sku_label"] = f"{sku.category} / {sku.brand} / {sku.model_name}"
        else:
            result["sku_label"] = None

        # 补充库位信息
        if db_item.location_id:
            location = get_location(self.db, db_item.location_id)
            if location:
                result["location_code"] = location.location_code
                result["location_name"] = location.location_name
            else:
                result["location_code"] = None
                result["location_name"] = None
        else:
            result["location_code"] = None
            result["location_name"] = None

        # 补充整机关联信息
        if db_item.machine_sn:
            siblings = get_active_items_by_machine_sn(self.db, db_item.machine_sn)
            result["machine_item_count"] = len(siblings)
            result["machine_siblings"] = [
                {"item_sn": s.item_sn, "status": s.status.value if hasattr(s.status, 'value') else s.status}
                for s in siblings if s.item_sn != item_sn
            ]
        else:
            result["machine_item_count"] = 0
            result["machine_siblings"] = []

        return result

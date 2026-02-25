from sqlalchemy.orm import Session
from database.crud.item_crud import create_item, get_item
from database.schemas.item_schema import ItemCreate, ItemResponse

class ItemService:
    def __init__(self, db: Session):
        self.db = db

    async def create_item_profile(self, item_data: ItemCreate):
        # 1. 检查 item_sn 是否已存在
        if get_item(self.db, item_data.item_sn):
            return {"error": f"Item SN {item_data.item_sn} already exists"}
        
        # 2. 创建物品
        db_item = create_item(self.db, item_data)
        # 转换为 Pydantic 模型再返回
        return ItemResponse.model_validate(db_item)

    async def get_item_detail(self, item_sn: str):
        db_item = get_item(self.db, item_sn)
        if not db_item:
            return None
        # 转换为 Pydantic 模型再返回
        return ItemResponse.model_validate(db_item)

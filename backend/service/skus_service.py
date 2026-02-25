# service/skus_service.py
from sqlalchemy.orm import Session
from database.schemas.sku_schema import SKUCreate
from database.crud import sku_crud  # 引入帮你干脏活累活的 crud 模块

class SKUService:
    def __init__(self, db: Session):
        self.db = db

    async def create_sku(self, query: SKUCreate):
        """
        录入标准配件档案的业务逻辑
        """
        # 1. 业务校验：调用 CRUD 查重
        existing_sku = sku_crud.get_sku_by_exact_match(
            self.db, 
            category=query.category, 
            brand=query.brand, 
            model_name=query.model_name
        )

        if existing_sku:
            return None  # 业务不通过，返回 None 给 Router 去报错
            
        # 2. 校验通过，调用 CRUD 写入数据库
        db_sku = sku_crud.create_sku(self.db, query)

        # 3. 组装给前端返回的数据
        return {
            "id": db_sku.id,
            "category": db_sku.category,
            "brand": db_sku.brand,
            "model_name": db_sku.model_name,
            "properties": db_sku.properties
        }

    async def search_skus(self, category: str, brand: str = None, keyword: str = "", limit: int = 10):
        """
        搜索 SKU 业务
        """
        # 直接调用 CRUD 获取原始数据
        skus = sku_crud.search_skus(self.db, category, brand, keyword, limit)

        # 业务层负责将原始数据转化成前端需要的列表格式
        result_list = [{"id": s.id, "model_name": s.model_name, "properties": s.properties} for s in skus]
        return result_list
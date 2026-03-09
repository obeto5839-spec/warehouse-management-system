import json
from sqlalchemy.orm import Session
from database.crud.order_crud import (
    create_order, get_order, get_orders, update_order, delete_order, count_orders_by_status, count_orders
)
from database.crud.sku_crud import get_sku_by_exact_match
from database.models.sku_model import SKU
from database.schemas.order_schema import OrderCreate, OrderUpdate, OrderResponse
from typing import Optional, List, Dict
from utils.log_manage import init_logger

logging = init_logger()


class OrderService:
    def __init__(self, db: Session):
        self.db = db

    async def create(self, data: OrderCreate):
        db_order = create_order(self.db, data)
        self._auto_learn_skus(data.order_type, data.config_detail)
        return OrderResponse.model_validate(db_order)

    def _auto_learn_skus(self, order_type: str, config_detail: str):
        """从订单配置中提取配件信息，自动将新品牌+型号写入 SKU 库"""
        if not config_detail:
            return
        try:
            items = self._extract_items(order_type, config_detail)
        except Exception as e:
            logging.warning(f"解析 config_detail 失败，跳过自动学习: {e}")
            return

        new_count = 0
        for item in items:
            category = item.get("category", "").strip()
            brand = item.get("brand", "").strip()
            model = item.get("model", "").strip()
            if not category or not brand or not model:
                continue
            existing = get_sku_by_exact_match(self.db, category, brand, model)
            if existing:
                continue
            specs = item.get("specs") or {}
            try:
                db_sku = SKU(
                    category=category,
                    brand=brand,
                    model_name=model,
                    properties=specs if specs else None,
                )
                self.db.add(db_sku)
                self.db.commit()
                new_count += 1
                logging.info(f"自动学习新 SKU: {category}/{brand}/{model}")
            except Exception as e:
                self.db.rollback()
                logging.warning(f"自动创建 SKU 失败({category}/{brand}/{model}): {e}")

        if new_count:
            logging.info(f"本次订单自动学习写入 {new_count} 条新 SKU")

    @staticmethod
    def _extract_items(order_type: str, config_detail: str) -> List[Dict]:
        """将不同订单类型的 config_detail JSON 统一提取为配件列表"""
        data = json.loads(config_detail)
        items = []
        if order_type == "台式整机" and isinstance(data, dict):
            for comp in data.get("components", []):
                items.append({
                    "category": comp.get("type", ""),
                    "brand": comp.get("brand", ""),
                    "model": comp.get("model", ""),
                    "specs": comp.get("specs"),
                })
            for ext in data.get("extras", []):
                items.append({
                    "category": ext.get("type", ""),
                    "brand": ext.get("brand", ""),
                    "model": ext.get("model", ""),
                    "specs": None,
                })
        elif order_type == "笔记本" and isinstance(data, dict):
            brand = data.get("brand", "").strip()
            series = data.get("series", "").strip()
            if brand and series:
                items.append({
                    "category": "笔记本",
                    "brand": brand,
                    "model": series,
                    "specs": {
                        k: data[k] for k in ("cpu", "gpu", "ram", "storage", "screen")
                        if data.get(k)
                    } or None,
                })
        elif order_type == "散件" and isinstance(data, list):
            for part in data:
                items.append({
                    "category": part.get("skuCategory", "") or part.get("type", ""),
                    "brand": part.get("brand", ""),
                    "model": part.get("model", ""),
                    "specs": part.get("specs"),
                })
        return items

    async def get(self, order_id: int):
        db_order = get_order(self.db, order_id)
        if not db_order:
            return None
        return OrderResponse.model_validate(db_order)

    async def list(self, skip: int = 0, limit: int = 50,
                   order_status: Optional[str] = None,
                   platform: Optional[str] = None,
                   customer_id: Optional[str] = None,
                   order_type: Optional[str] = None):
        items = get_orders(self.db, skip, limit, order_status, platform, customer_id, order_type)
        return [OrderResponse.model_validate(i) for i in items]

    async def count(self, order_status: Optional[str] = None,
                    platform: Optional[str] = None,
                    customer_id: Optional[str] = None,
                    order_type: Optional[str] = None) -> int:
        return count_orders(self.db, order_status, platform, customer_id, order_type)

    async def update(self, order_id: int, data: OrderUpdate):
        db_order = update_order(self.db, order_id, data)
        if not db_order:
            return {"error": "订单不存在"}
        return OrderResponse.model_validate(db_order)

    async def delete(self, order_id: int):
        db_order = delete_order(self.db, order_id)
        if not db_order:
            return {"error": "订单不存在"}
        return {"message": "删除成功"}

    async def stats(self):
        return count_orders_by_status(self.db)

from sqlalchemy.orm import Session
from database.crud.item_crud import (
    get_items_by_machine_sn,
    get_active_items_by_machine_sn,
    unbind_machine,
    batch_update_machine_status,
    get_item,
    update_item,
)
from database.crud.outbound_crud import create_outbound_record
from database.schemas.item_schema import ItemResponse, ItemUpdate, ItemStatus
from database.schemas.outbound_schema import OutboundRecordCreate
from decimal import Decimal


class MachineService:
    def __init__(self, db: Session):
        self.db = db

    async def get_machine_items(self, machine_sn: str):
        """查询整机下的所有配件"""
        items = get_items_by_machine_sn(self.db, machine_sn)
        if not items:
            return {"error": "整机编码不存在或无绑定配件"}
        return [ItemResponse.model_validate(item) for item in items]

    async def ship_machine(self, machine_sn: str, order_no: str, sell_price: Decimal, buyer_info: str = None):
        """
        整机一键出库
        扫整机码 → 找到所有配件 → 全部标记已售 → 生成出库记录
        """
        items = get_active_items_by_machine_sn(self.db, machine_sn)
        if not items:
            return {"error": "整机编码不存在或所有配件已售出"}

        # 计算总成本
        total_cost = sum(item.cost_price or 0 for item in items)

        # 为每个配件创建出库记录
        records = []
        per_price = sell_price / len(items) if len(items) > 0 else 0
        for item in items:
            record_data = OutboundRecordCreate(
                order_no=order_no,
                item_sn=item.item_sn,
                sell_price=per_price,
                buyer_info=buyer_info,
            )
            record = create_outbound_record(self.db, record_data)
            records.append(record)

        # 批量更新状态为已售
        batch_update_machine_status(self.db, machine_sn, "sold")

        return {
            "machine_sn": machine_sn,
            "order_no": order_no,
            "item_count": len(items),
            "total_cost": float(total_cost),
            "sell_price": float(sell_price),
            "profit": float(sell_price - total_cost),
            "items": [item.item_sn for item in items],
        }

    async def unbind_and_sell(self, item_sn: str, order_no: str, sell_price: Decimal, buyer_info: str = None):
        """
        拆件出库：从整机中解绑单个配件并出库
        扫配件码 → 检查是否在整机中 → 提示确认 → 解绑 + 出库
        """
        item = get_item(self.db, item_sn)
        if not item:
            return {"error": "配件不存在"}
        if item.status == "sold":
            return {"error": "配件已售出"}

        machine_info = None
        if item.machine_sn:
            remaining = get_active_items_by_machine_sn(self.db, item.machine_sn)
            remaining_count = len([i for i in remaining if i.item_sn != item_sn])
            machine_info = {
                "machine_sn": item.machine_sn,
                "remaining_count": remaining_count,
            }

        # 解绑
        unbind_machine(self.db, item_sn)

        # 出库
        record_data = OutboundRecordCreate(
            order_no=order_no,
            item_sn=item_sn,
            sell_price=sell_price,
            buyer_info=buyer_info,
        )
        create_outbound_record(self.db, record_data)

        # 更新状态
        update_item(self.db, item_sn, ItemUpdate(status=ItemStatus.SOLD, location_id=None))

        return {
            "item_sn": item_sn,
            "order_no": order_no,
            "sell_price": float(sell_price),
            "machine_info": machine_info,
        }

    async def check_machine_binding(self, item_sn: str):
        """
        检查配件是否属于某台整机（出库前的提示用）
        """
        item = get_item(self.db, item_sn)
        if not item:
            return {"error": "配件不存在"}

        if not item.machine_sn:
            return {"is_bound": False, "machine_sn": None, "siblings": []}

        siblings = get_active_items_by_machine_sn(self.db, item.machine_sn)
        return {
            "is_bound": True,
            "machine_sn": item.machine_sn,
            "siblings": [ItemResponse.model_validate(s) for s in siblings],
        }

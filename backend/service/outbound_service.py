from sqlalchemy.orm import Session
from database.crud.outbound_crud import create_outbound_record, get_outbound_records
from database.crud.item_crud import get_item, update_item
from database.schemas.outbound_schema import OutboundRecordCreate
from database.schemas.item_schema import ItemUpdate, ItemStatus

class OutboundService:
    def __init__(self, db: Session):
        self.db = db

    async def execute_shipping(self, query: OutboundRecordCreate):
        """执行发货"""
        # 1. 检查物品
        item = get_item(self.db, query.item_sn)
        if not item:
            return {"error": "Item not found"}
        
        if item.status == ItemStatus.SOLD:
             return {"error": "Item already sold"}

        # 2. 创建出库记录
        record = create_outbound_record(self.db, query)
        
        # 3. 更新物品状态为已售，并从库位移除
        item_update = ItemUpdate(
            status=ItemStatus.SOLD,
            location_id=None
        )
        update_item(self.db, item.item_sn, item_update)
        
        return record

    async def get_order_detail(self, order_no: str):
        # 简单实现：只返回第一条记录，实际可能一个订单有多条
        records = get_outbound_records(self.db, order_no=order_no)
        return records

    async def get_outbound_list(self, item_sn=None, skip=0, limit=10):
        return get_outbound_records(self.db, skip=skip, limit=limit)

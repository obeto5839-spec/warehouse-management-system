from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

class OutboundRecordBase(BaseModel):
    order_no: str = Field(..., description="订单号")
    item_sn: str = Field(..., description="关联 items 表的 item_sn")
    sell_price: Decimal = Field(..., description="实际售出价格")
    buyer_info: Optional[str] = Field(None, description="买家信息或备注")

class OutboundRecordCreate(OutboundRecordBase):
    pass

class OutboundRecordUpdate(BaseModel):
    order_no: Optional[str] = None
    sell_price: Optional[Decimal] = None
    buyer_info: Optional[str] = None

class OutboundRecordResponse(OutboundRecordBase):
    id: int
    outbound_time: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

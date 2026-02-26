from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from decimal import Decimal
from enum import Enum

# 与 Model 中的枚举保持一致
class ItemStatus(str, Enum):
    PENDING_SHELVING = "pending_shelving"
    IN_STOCK = "in_stock"
    SOLD = "sold"
    FROZEN = "frozen"
    MAINTENANCE = "maintenance"

class ItemBase(BaseModel):
    sku_id: int = Field(..., description="关联的标准配件ID")
    grade: Optional[str] = Field(None, description="成色，例如：99新")
    factory_sn: Optional[str] = Field(None, description="原厂条码")
    cost_price: Optional[Decimal] = Field(0.00, description="回收成本价")
    machine_sn: Optional[str] = Field(None, description="整机编码，空表示散件")
    location_id: Optional[int] = Field(None, description="库位ID")

class ItemCreate(ItemBase):
    item_sn: str = Field(..., description="内部唯一编码/二维码内容")

class ItemUpdate(BaseModel):
    grade: Optional[str] = None
    factory_sn: Optional[str] = None
    cost_price: Optional[Decimal] = None
    status: Optional[ItemStatus] = None
    machine_sn: Optional[str] = None
    location_id: Optional[int] = None

class ItemResponse(ItemBase):
    item_sn: str
    status: ItemStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

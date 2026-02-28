from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class OrderCreate(BaseModel):
    platform: str = Field(..., description="回收渠道")
    customer_id: str = Field(..., description="卖家ID")
    phone: Optional[str] = Field(None, description="卖家电话")
    region: Optional[str] = Field(None, description="发货区域")
    order_type: str = Field(..., description="物品大类")
    config_detail: Optional[str] = Field(None, description="配置详情JSON")
    condition_grade: Optional[str] = Field(None, description="成色鉴定")
    functional_status: Optional[str] = Field(None, description="功能状态")
    price: Optional[float] = Field(0, description="预估回收价格")
    shipping_method: Optional[str] = Field(None, description="发货方式")
    payment_amount: Optional[float] = Field(0, description="应付打款金额")
    shipping_fee: Optional[float] = Field(0, description="我方承担运费")
    order_status: str = Field("待收货", description="订单状态")
    notes: Optional[str] = Field(None, description="备注")


class OrderUpdate(BaseModel):
    platform: Optional[str] = None
    customer_id: Optional[str] = None
    phone: Optional[str] = None
    region: Optional[str] = None
    order_type: Optional[str] = None
    config_detail: Optional[str] = None
    condition_grade: Optional[str] = None
    functional_status: Optional[str] = None
    price: Optional[float] = None
    shipping_method: Optional[str] = None
    payment_amount: Optional[float] = None
    shipping_fee: Optional[float] = None
    order_status: Optional[str] = None
    notes: Optional[str] = None


class OrderResponse(BaseModel):
    id: int
    platform: str
    customer_id: str
    phone: Optional[str] = None
    region: Optional[str] = None
    order_type: str
    config_detail: Optional[str] = None
    condition_grade: Optional[str] = None
    functional_status: Optional[str] = None
    price: Optional[float] = None
    shipping_method: Optional[str] = None
    payment_amount: Optional[float] = None
    shipping_fee: Optional[float] = None
    order_status: str
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

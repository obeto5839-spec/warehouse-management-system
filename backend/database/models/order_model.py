from sqlalchemy import Column, Integer, String, Numeric, Text, DateTime, Enum as SAEnum
from sqlalchemy.sql import func
from database.models.base import Base
import enum


class OrderType(enum.Enum):
    DESKTOP = "台式整机"
    LAPTOP = "笔记本"
    PARTS = "散件"


class ShippingMethod(enum.Enum):
    SF = "顺丰"
    NORMAL = "普通快递"
    SELF = "上门自提"


class OrderStatus(enum.Enum):
    PAID_IN_TRANSIT = "已打款，在途中"
    UNPAID_IN_TRANSIT = "未打款，在途中"
    PAID_STOCKED = "已打款，入库完毕"
    RETURNED = "验机不符，退货拦截"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # 客户(卖家)信息
    platform = Column(String(50), nullable=False, comment="回收渠道")
    customer_id = Column(String(100), nullable=False, comment="卖家ID/昵称")
    phone = Column(String(20), nullable=True, comment="卖家联系电话")
    region = Column(String(100), nullable=True, comment="发货区域")

    # 配件信息
    order_type = Column(
        SAEnum(OrderType, values_callable=lambda x: [e.value for e in x]),
        nullable=False, comment="物品大类"
    )
    config_detail = Column(Text, nullable=True, comment="配置详情(JSON)")
    condition_grade = Column(String(50), nullable=True, comment="成色鉴定")
    functional_status = Column(String(50), nullable=True, comment="功能状态")
    price = Column(Numeric(10, 2), nullable=True, default=0, comment="预估回收价格")

    # 物流结算
    shipping_method = Column(
        SAEnum(ShippingMethod, values_callable=lambda x: [e.value for e in x]),
        nullable=True, comment="发货方式"
    )
    payment_amount = Column(Numeric(10, 2), nullable=True, default=0, comment="应付打款金额")
    shipping_fee = Column(Numeric(10, 2), nullable=True, default=0, comment="我方承担运费")
    order_status = Column(
        SAEnum(OrderStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False, default=OrderStatus.UNPAID_IN_TRANSIT.value, comment="订单状态"
    )

    notes = Column(Text, nullable=True, comment="备注")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

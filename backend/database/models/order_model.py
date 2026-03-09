from sqlalchemy import Column, Integer, String, Numeric, Text, DateTime
from sqlalchemy.sql import func
from database.models.base import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # 客户(卖家)信息
    platform = Column(String(50), nullable=False, comment="回收渠道")
    customer_id = Column(String(100), nullable=False, comment="卖家ID/昵称")
    phone = Column(String(20), nullable=True, comment="卖家联系电话")
    region = Column(String(100), nullable=True, comment="发货区域")

    # 配件信息
    order_type = Column(String(50), nullable=False, comment="物品大类：台式整机/笔记本/散件")
    config_detail = Column(Text, nullable=True, comment="配置详情(JSON)")
    condition_grade = Column(String(50), nullable=True, comment="成色鉴定")
    functional_status = Column(String(50), nullable=True, comment="功能状态")
    price = Column(Numeric(10, 2), nullable=True, default=0, comment="预估回收价格")

    # 物流结算
    shipping_method = Column(String(50), nullable=True, comment="发货方式：顺丰/普通快递/上门自提")
    payment_amount = Column(Numeric(10, 2), nullable=True, default=0, comment="应付打款金额")
    shipping_fee = Column(Numeric(10, 2), nullable=True, default=0, comment="我方承担运费")
    order_status = Column(String(50), nullable=False, default="未打款，在途中", comment="订单状态")

    notes = Column(Text, nullable=True, comment="备注")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

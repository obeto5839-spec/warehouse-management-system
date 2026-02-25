from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.models.base import Base

class OutboundRecord(Base):
    """
    出货/订单表 (outbound_records)
    记录交易和出库信息，“卖给谁了，卖了多少钱”
    """
    __tablename__ = "outbound_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_no = Column(String(50), index=True, nullable=False, comment="订单号")
    
    # 关联到具体的 Item
    item_sn = Column(String(50), ForeignKey("items.item_sn"), nullable=False, index=True, comment="关联 items 表的 item_sn")
    
    sell_price = Column(DECIMAL(10, 2), nullable=False, comment="实际售出价格")
    buyer_info = Column(String(200), nullable=True, comment="买家信息或备注")
    
    outbound_time = Column(DateTime(timezone=True), server_default=func.now(), comment="出库时间")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关联关系
    item = relationship("Item", backref="outbound_records")

    def __repr__(self):
        return f"<OutboundRecord(order_no='{self.order_no}', item_sn='{self.item_sn}', sell_price={self.sell_price})>"

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from database.models.base import Base

# 定义物品状态枚举
class ItemStatus(enum.Enum):
    PENDING_SHELVING = "pending_shelving"  # 待上架
    IN_STOCK = "in_stock"                  # 在库
    SOLD = "sold"                          # 已出库/已售
    FROZEN = "frozen"                      # 冻结/预占（如下单未发货）
    MAINTENANCE = "maintenance"            # 维修中/损耗

class Item(Base):
    """
    具体物件表 (items)
    最核心的“一物一码”表，每一个实体配件在这里都有一行唯一的数据
    """
    __tablename__ = "items"

    # item_sn 既是主键也是内部唯一编码
    item_sn = Column(String(50), primary_key=True, index=True, nullable=False, comment="内部唯一编码/二维码内容")
    
    sku_id = Column(Integer, ForeignKey("skus.id"), nullable=False, index=True, comment="关联 skus 表的 id")
    
    grade = Column(String(50), nullable=True, comment="成色，例如：99新、95新")
    factory_sn = Column(String(100), nullable=True, index=True, comment="原厂条码，选填")
    cost_price = Column(DECIMAL(10, 2), default=0.00, comment="回收成本价")
    
    status = Column(
        Enum(ItemStatus, values_callable=lambda x: [e.value for e in x]),
        default=ItemStatus.PENDING_SHELVING,
        index=True,
        comment="当前状态"
    )
    
    # 启用外键约束
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True, comment="库位ID，空表示未上架") 
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关联关系
    sku = relationship("SKU", backref="items")
    # location 关系已经在 Location 模型中通过 backref 定义了，这里不需要重复定义，或者可以使用 back_populates
    # 如果想在这里显式定义，可以使用:
    # location = relationship("Location", back_populates="items")

    def __repr__(self):
        return f"<Item(sn='{self.item_sn}', sku_id={self.sku_id}, status='{self.status}')>"

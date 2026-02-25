from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql import func
from database.models.base import Base

class SKU(Base):
    """
    标准配件表 (skus)
    这张表用来定义标准产品（比如所有的 RTX 3060 都在这里只有一条记录）
    """
    __tablename__ = "skus"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category = Column(String(50), index=True, nullable=False, comment="分类，例如：显卡、CPU、主板")
    brand = Column(String(50), index=True, nullable=False, comment="品牌，例如：微星、华硕、Intel")
    model_name = Column(String(100), index=True, nullable=False, comment="型号，例如：RTX 3060 12G、i5-13400F")
    
    # 扩展属性，预留给不同配件的特殊参数
    # 例如 内存: {"frequency": "3200MHz", "type": "DDR4"}
    # 例如 显卡: {"memory_size": "12G", "chipset": "NVIDIA"}
    properties = Column(JSON, nullable=True, comment="扩展属性，JSON格式")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<SKU(id={self.id}, category='{self.category}', model_name='{self.model_name}')>"

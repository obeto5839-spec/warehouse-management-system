from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql import func
from database.models.base import Base

class SKU(Base):
    """
    标准配件表 (skus)
    这张表用来定义标准产品（比如所有的 RTX 3060 都在这里只有一条记录）
    SKU 命名规则：品牌 + 系列 + 型号 + 规格
    例如：华硕(品牌) 雪豹(系列) RTX 4060 Ti(型号) O16G(规格)
    """
    __tablename__ = "skus"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category = Column(String(50), index=True, nullable=False, comment="分类，例如：显卡、CPU、主板")
    brand = Column(String(50), index=True, nullable=False, comment="品牌，例如：华硕、英特尔、联力")
    series = Column(String(100), index=True, nullable=True, comment="系列，例如：雪豹、酷睿、ROG STRIX")
    model_name = Column(String(100), index=True, nullable=False, comment="型号，例如：RTX 4060 Ti、i5-13490F、B760I GAMING")
    
    # 规格信息，简单文本描述
    # 例如 显卡: {"spec": "O16G"}
    # 例如 内存: {"spec": "32G(16*2)6400C32", "spec2": "海力士A-DIE"}
    properties = Column(JSON, nullable=True, comment="规格参数，JSON格式")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<SKU(id={self.id}, category='{self.category}', model_name='{self.model_name}')>"

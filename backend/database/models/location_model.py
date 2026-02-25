from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from database.models.base import Base

class Location(Base):
    """
    库位表 (locations)
    用于管理物理仓库的货架
    """
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    location_code = Column(String(50), unique=True, index=True, nullable=False, comment="库位编码，例如：A-03-02")
    location_name = Column(String(100), nullable=True, comment="库位名称，例如：显卡良品区")
    
    # 树状层级结构 (Self-referential)
    # parent_id 为空表示顶级区域（如：A区），不为空表示子区域（如：3号架）
    parent_id = Column(Integer, ForeignKey("locations.id"), nullable=True, comment="父级库位ID")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关联关系：自引用树状结构
    parent = relationship(
        "Location",
        remote_side=[id],
        backref=backref("children", cascade="all, delete-orphan")
    )
    items = relationship("Item", backref="location")

    def __repr__(self):
        return f"<Location(code='{self.location_code}', name='{self.location_name}')>"

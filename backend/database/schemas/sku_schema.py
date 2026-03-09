from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class SKUBase(BaseModel):
    category: str = Field(..., description="分类，例如：显卡、CPU、主板")
    brand: str = Field(..., description="品牌，例如：华硕、英特尔、联力")
    series: Optional[str] = Field(default=None, description="系列，例如：雪豹、酷睿、ROG STRIX")
    model_name: str = Field(..., description="型号，例如：RTX 4060 Ti、i5-13490F")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict, description="规格参数，JSON格式")
    model_config = {
        "protected_namespaces": ()
    }

class SKUCreate(SKUBase):
    pass

class SKUUpdate(BaseModel):
    category: Optional[str] = None
    brand: Optional[str] = None
    series: Optional[str] = None
    model_name: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None

class SKUResponse(SKUBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

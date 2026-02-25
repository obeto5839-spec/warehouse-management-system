from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Dict, Any
from utils.sku_validator import validate_sku_properties
from datetime import datetime

class SKUBase(BaseModel):
    category: str = Field(..., description="分类，例如：显卡、CPU、主板")
    brand: str = Field(..., description="品牌，例如：微星、华硕、Intel")
    model_name: str = Field(..., description="型号，例如：RTX 3060 12G")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict, description="扩展属性，JSON格式")
    model_config = {
        "protected_namespaces": ()
    }
    @model_validator(mode='after')
    def check_properties_compliance(self) -> 'SKUBase':
        """
        校验 properties 是否符合 category 的规范
        """
        category = self.category
        properties = self.properties
        
        is_valid, error_msg = validate_sku_properties(category, properties)
        if not is_valid:
            raise ValueError(error_msg)
            
        return self

class SKUCreate(SKUBase):
    pass

class SKUUpdate(BaseModel):
    category: Optional[str] = None
    brand: Optional[str] = None
    model_name: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None

class SKUResponse(SKUBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

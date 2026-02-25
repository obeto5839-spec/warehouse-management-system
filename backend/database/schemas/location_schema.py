from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class LocationBase(BaseModel):
    location_code: str = Field(..., description="库位编码，例如：A-03-02")
    location_name: Optional[str] = Field(None, description="库位名称，例如：显卡良品区")
    parent_id: Optional[int] = Field(None, description="父级库位ID")

class LocationCreate(LocationBase):
    pass

class LocationUpdate(BaseModel):
    location_code: Optional[str] = None
    location_name: Optional[str] = None
    parent_id: Optional[int] = None

class LocationResponse(LocationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

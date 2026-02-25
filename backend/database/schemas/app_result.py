from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, Any

T = TypeVar("T")

class AppResult(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: Optional[T] = None

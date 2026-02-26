from typing import Optional
from datetime import datetime
from pydantic import BaseModel, field_serializer


class FunctionBase(BaseModel):
    func_name: str
    uri: Optional[str] = None
    status: Optional[str] = '0'
    method_type: Optional[str] = None
    group: Optional[str] = None


class FunctionCreate(FunctionBase):
    group_id: int


class FunctionUpdate(BaseModel):
    group_id: Optional[int] = None


class FunctionInDB(FunctionBase):
    func_id: int
    group_id: int
    ctime: Optional[datetime] = None
    utime: Optional[datetime] = None

    @field_serializer('ctime')
    def serialize_ctime(self, dt: datetime) -> str:
        if dt is not None:
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        return None

    @field_serializer('utime')
    def serialize_utime(self, dt: datetime) -> str:
        if dt is not None:
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        return None

    model_config = {
        "from_attributes": True
    }


class Function(FunctionInDB):
    class Config:
        from_attributes = True

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, field_serializer


class ComponentBase(BaseModel):
    component_name: str


class ComponentCreate(ComponentBase):
    group_id: int


class ComponentUpdate(BaseModel):
    component_name: Optional[str] = None
    group_id: Optional[int] = None
    status: Optional[str] = None


class ComponentInDB(ComponentBase):
    component_id: Optional[int] = None
    status: Optional[str] = None
    group: Optional[str] = None
    group_id: Optional[int] = None
    ctime: datetime
    utime: datetime

    @field_serializer('ctime')
    def serialize_ctime(self, dt: datetime) -> Optional[str]:
        if dt is not None:
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        return None

    @field_serializer('utime')
    def serialize_utime(self, dt: datetime) -> Optional[str]:
        if dt is not None:
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        return None

    model_config = {
        "from_attributes": True
    }


class Component(ComponentInDB):
    pass

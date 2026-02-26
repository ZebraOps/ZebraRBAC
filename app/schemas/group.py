from typing import Optional
from datetime import datetime
from pydantic import BaseModel, field_serializer


class GroupBase(BaseModel):
    status: str
    group_name: str
    description: Optional[str] = None


class GroupCreate(GroupBase):
    pass


class GroupUpdate(BaseModel):
    status: Optional[str] = None
    group_name: Optional[str] = None
    description: Optional[str] = None


class GroupInDB(GroupBase):
    group_id: int
    status: str
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


class Group(GroupInDB):
    pass

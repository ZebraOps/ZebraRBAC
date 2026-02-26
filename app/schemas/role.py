from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, field_serializer

from app.schemas.user import User


class RoleBase(BaseModel):
    role_name: str
    role_desc: Optional[str] = None
    status: Optional[str] = "0"
    group_id: int
    projects: Optional[str] = None
    group: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    role_name: Optional[str] = None
    role_desc: Optional[str] = None
    status: Optional[str] = None
    group_id: Optional[int] = None
    projects: Optional[str] = None


class RoleInDB(RoleBase):
    role_id: int
    ctime: Optional[datetime] = None
    utime: Optional[datetime] = None

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


class RoleWithUsers(RoleInDB):
    """
    包含用户信息的角色模型
    """
    users: List[User] = []


class Role(RoleInDB):
    pass

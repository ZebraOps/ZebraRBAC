from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, field_serializer

from app.schemas.user import User
from app.schemas.organization import Organization
from app.schemas.position import Position


class UserOrganizationResponse(BaseModel):
    id: int
    user_id: int
    org_id: int
    position_id: int
    is_primary: Optional[int] = 0
    ctime: Optional[datetime] = None
    utime: Optional[datetime] = None

    # 关联对象
    user: Optional[User] = None
    organization: Optional[Organization] = None
    position: Optional[Position] = None

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

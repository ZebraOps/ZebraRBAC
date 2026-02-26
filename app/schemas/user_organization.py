from typing import Optional
from datetime import datetime
from pydantic import BaseModel, field_serializer


class UserOrganizationBase(BaseModel):
    user_id: int
    org_id: int
    position_id: int
    is_primary: Optional[int] = 0


class UserOrganizationCreate(UserOrganizationBase):
    pass


class UserOrganizationUpdate(BaseModel):
    is_primary: Optional[int] = None


class UserOrganizationInDB(UserOrganizationBase):
    id: int
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


class UserOrganization(UserOrganizationInDB):
    # 使用字符串注解避免循环引用
    # 不在模型定义中直接引用其他模型，而是在实际使用时处理
    pass

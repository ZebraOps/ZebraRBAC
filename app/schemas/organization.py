from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, field_serializer, validator


class OrganizationBase(BaseModel):
    org_name: str
    org_code: str
    org_type: Optional[int] = 1  # 1-组织，2-部门，3-团队
    parent_id: Optional[int] = None
    level: Optional[int] = None
    order_num: Optional[int] = 0


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    org_name: Optional[str] = None
    org_code: Optional[str] = None
    org_type: Optional[int] = None
    parent_id: Optional[int] = None
    level: Optional[int] = None
    order_num: Optional[int] = None

    @validator('parent_id')
    def validate_parent_id(cls, v):
        # 将 0 转换为 None
        if v == 0:
            return None
        return v


class OrganizationInDB(OrganizationBase):
    org_id: int
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


class OrganizationTree(OrganizationInDB):
    children: Optional[List['OrganizationTree']] = None  # 改为 Optional

    @field_serializer('children')
    def serialize_children(self, children: Optional[List['OrganizationTree']]) -> Optional[List['OrganizationTree']]:
        # 如果 children 为空列表或 None，返回 None
        if not children:
            return None
        return children

# 解决循环引用
OrganizationTree.model_rebuild()


class Organization(OrganizationInDB):
    pass

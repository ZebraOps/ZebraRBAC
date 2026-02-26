from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, field_serializer


class MenuBase(BaseModel):
    menu_name: str
    status: Optional[str] = "0"
    path: Optional[str] = None
    parent_id: Optional[int] = None
    order_num: Optional[int] = 0
    icon: Optional[str] = None


class MenuCreate(MenuBase):
    pass


class MenuUpdate(BaseModel):
    menu_name: Optional[str] = None
    status: Optional[str] = None
    path: Optional[str] = None
    parent_id: Optional[int] = None
    order_num: Optional[int] = None
    icon: Optional[str] = None


class MenuInDB(MenuBase):
    menu_id: int
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


class MenuTree(MenuInDB):
    """
    菜单树状结构
    """
    children: List["MenuTree"] = []


# 更新 forward references
MenuTree.model_rebuild()


class Menu(MenuInDB):
    pass

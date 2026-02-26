from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, field_serializer


class UserBase(BaseModel):
    username: Optional[str] = None
    nickname: Optional[str] = None
    email:Optional[EmailStr] = None
    tel: Optional[str] = None
    wechat: Optional[str] = None
    department: Optional[str] = None
    gender: Optional[str] = None
    avatar: Optional[str] = None
    role_ids: Optional[List[int]] = None
    job_ids: Optional[List[int]] = None


class UserCreate(UserBase):
    password: Optional[str] = None
    superuser: Optional[str] = "10"
    status: Optional[str] = "0"


class UserUpdate(UserBase):
    status: Optional[str] = None
    superuser: Optional[str] = None
    password: Optional[str] = None


class UserUpdatePassword(BaseModel):
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserInDB(UserBase):
    user_id: int
    superuser: str
    status: str
    employee_id: Optional[str] = None
    last_ip: Optional[str] = None
    last_login: Optional[datetime] = None
    disable_at: Optional[datetime] = None
    ctime: datetime
    wechat_userid: Optional[str] = None
    dingtalk_userid: Optional[str] = None
    feishu_userid: Optional[str] = None
    dept: Optional[Dict[str, Any]] = None

    model_config = {
        "from_attributes": True
    }

    @field_serializer('last_login', 'disable_at', 'ctime')
    def serialize_datetime(self, dt: datetime) -> str:
        if dt:
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        return None


class User(UserInDB):
    pass

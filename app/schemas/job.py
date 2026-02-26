# app/schemas/job.py
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, field_serializer


class JobBase(BaseModel):
    job_name: str
    description: Optional[str] = None


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    job_name: Optional[str] = None
    description: Optional[str] = None


class JobInDB(JobBase):
    job_id: int
    job_code: Optional[str] = None
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


class Job(JobInDB):
    pass

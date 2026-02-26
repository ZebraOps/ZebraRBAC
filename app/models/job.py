# app/models/job.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.session import Base


class Job(Base):
    __tablename__ = "jobs"

    job_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    job_code = Column(String(50), unique=True, index=True, comment="岗位编码")
    job_name = Column(String(100), comment="岗位名称")
    description = Column(String(255), comment="岗位描述")
    ctime = Column(DateTime, default=datetime.now, comment="创建时间")
    utime = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系
    job_users = relationship("UserJob", back_populates="job", overlaps="roles,users")

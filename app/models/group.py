from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.session import Base


class Group(Base):
    __tablename__ = "groups"

    group_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    group_name = Column(String(50), unique=True, index=True, comment="分组名称")
    description = Column(String(200), comment="分组描述")
    status = Column(String(5), default="0", comment="状态：0-正常，1-禁用")
    ctime = Column(DateTime, default=datetime.now, comment="创建时间")
    utime = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系
    roles = relationship("Role", backref="group_relation")
    functions = relationship("Function", backref="group_relation")
    components = relationship("Component", backref="group_relation")

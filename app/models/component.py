from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.session import Base


class Component(Base):
    __tablename__ = "components"

    component_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    component_name = Column(String(50), unique=True, index=True, comment="组件名称")
    status = Column(String(5), default="0", comment="状态：0-正常，1-禁用")
    ctime = Column(DateTime, default=datetime.now, comment="创建时间")
    utime = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    group = Column(String(50), nullable=True, comment="分组名称")
    group_id = Column(Integer, ForeignKey("groups.group_id"), comment="分组ID")

    # 关系
    roles = relationship("RoleComponent", back_populates="component")

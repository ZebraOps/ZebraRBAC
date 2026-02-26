from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.session import Base


class Function(Base):
    __tablename__ = "functions"

    func_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    func_name = Column(String(50), unique=True, index=True, comment="功能名称")
    uri = Column(String(256), unique=True, index=True, comment="功能接口")
    status = Column(String(5), default="0", comment="状态：0-正常，1-禁用")
    ctime = Column(DateTime, default=datetime.now, comment="创建时间")
    utime = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    method_type = Column(String(10), nullable=True, comment="请求方法")
    group = Column(String(50), nullable=True, comment="分组名称")
    group_id = Column(Integer, ForeignKey("groups.group_id"), comment="分组ID")

    # 关系
    # group由backref提供
    roles = relationship("RoleFunction", back_populates="function")

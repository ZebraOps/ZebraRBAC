from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.session import Base


class Role(Base):
    __tablename__ = "roles"

    role_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    role_name = Column(String(50), unique=True, index=True, comment="角色名称")
    role_desc = Column(Text, comment="角色描述")  # 修改为Text类型并添加备注
    status = Column(String(5), default="0", comment="状态：0-正常，1-禁用")
    ctime = Column(DateTime, default=datetime.now, comment="创建时间")
    utime = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    projects = Column(String(255), comment="项目列表")
    group = Column(String(50), nullable=True, comment="分组名称")
    group_id = Column(Integer, ForeignKey("groups.group_id"), comment="分组ID")

    # 关系
    role_users = relationship("UserRole", back_populates="role", overlaps="roles,users")
    menus = relationship("RoleMenu", back_populates="role")
    functions = relationship("RoleFunction", back_populates="role")
    components = relationship("RoleComponent", back_populates="role")

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.session import Base


class Menu(Base):
    __tablename__ = "menus"

    menu_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    menu_name = Column(String(50), unique=True, index=True, comment="菜单名称")
    path = Column(String(256), unique=True, index=True, nullable=True, comment="菜单地址")
    status = Column(String(5), default="0", comment="状态：0-正常，1-禁用")
    ctime = Column(DateTime, default=datetime.now, comment="创建时间")
    utime = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    parent_id = Column(Integer, ForeignKey("menus.menu_id"), nullable=True, comment="父菜单ID")
    order_num = Column(Integer, default=0, comment="排序字段")
    icon = Column(String(50), nullable=True, comment="菜单图标")

    # 关系
    children = relationship("Menu", back_populates="parent")
    parent = relationship("Menu", back_populates="children", remote_side=[menu_id])
    roles = relationship("RoleMenu", back_populates="menu")

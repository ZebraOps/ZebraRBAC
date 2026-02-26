from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.session import Base


class RoleMenu(Base):
    __tablename__ = "role_menus"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey("roles.role_id"))
    menu_id = Column(Integer, ForeignKey("menus.menu_id"))
    ctime = Column(DateTime, default=datetime.now, comment="创建时间")
    utime = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系
    role = relationship("Role", back_populates="menus")
    menu = relationship("Menu", back_populates="roles")

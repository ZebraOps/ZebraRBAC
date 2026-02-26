from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.session import Base


class RoleFunction(Base):
    __tablename__ = "role_functions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey("roles.role_id"))
    func_id = Column(Integer, ForeignKey("functions.func_id"))
    ctime = Column(DateTime, default=datetime.now, comment="创建时间")
    utime = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系
    role = relationship("Role", back_populates="functions")
    function = relationship("Function", back_populates="roles")

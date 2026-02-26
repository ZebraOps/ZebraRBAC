from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.session import Base


class Position(Base):
    __tablename__ = "positions"

    position_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    position_name = Column(String(100), index=True, comment="职务名称")
    position_code = Column(String(50), unique=True, comment="职务编码")
    description = Column(Text, comment="职务描述")
    ctime = Column(DateTime, default=datetime.now, comment="创建时间")
    utime = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系
    user_orgs = relationship("UserOrganization", back_populates="position")

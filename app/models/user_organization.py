from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.session import Base


class UserOrganization(Base):
    __tablename__ = "user_organizations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    org_id = Column(Integer, ForeignKey("organizations.org_id"))
    position_id = Column(Integer, ForeignKey("positions.position_id"))
    is_primary = Column(Integer, default=0, comment="是否主岗：0-否，1-是")
    ctime = Column(DateTime, default=datetime.now, comment="创建时间")
    utime = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系
    user = relationship("User", backref="user_organizations")
    organization = relationship("Organization", back_populates="user_orgs")
    position = relationship("Position", back_populates="user_orgs")

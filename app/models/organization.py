from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.session import Base


class Organization(Base):
    __tablename__ = "organizations"

    org_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    org_name = Column(String(100), index=True, comment="组织名称")
    org_code = Column(String(50), unique=True, comment="组织编码")
    org_type = Column(Integer, default=2, comment="组织类型：1-组织，2-部门，3-团队，4-团队")
    parent_id = Column(Integer, ForeignKey("organizations.org_id"), nullable=True, comment="父级组织ID")
    level = Column(Integer, comment="组织层级")
    order_num = Column(Integer, default=0, comment="显示顺序")
    ctime = Column(DateTime, default=datetime.now, comment="创建时间")
    utime = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系
    parent = relationship("Organization", remote_side=[org_id], backref="children")
    user_orgs = relationship("UserOrganization", back_populates="organization")

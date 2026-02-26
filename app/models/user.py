from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, comment="英文名称")
    password = Column(String(100), comment="用户密码")
    nickname = Column(String(100), comment="中文名称")
    email = Column(String(80), unique=True, index=True, comment="邮箱地址")
    employee_id = Column(String(50), unique=True, index=True, comment="工号")
    gender = Column(String(10), comment="性别")
    tel = Column(String(11), comment="电话号码")
    wechat = Column(String(50), comment="微信名称")
    department = Column(String(50), comment="主部门")
    superuser = Column(String(5), default="10", comment="管理员")  # 0表示超级用户
    status = Column(String(5), default="0", comment="状态：0-正常，1-禁用")
    last_ip = Column(String(20), default="", comment="最后登录IP")
    last_login = Column(DateTime, default=datetime.now, comment="最后登录时间")
    disable_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="禁用时间")
    wechat_userid = Column(String(50), comment="微信ID")
    dingtalk_userid = Column(String(50), comment="钉钉ID")
    feishu_userid = Column(String(50), comment="飞书ID")
    avatar = Column(String(256), comment="头像地址")
    ctime = Column(DateTime, default=datetime.now, comment="创建时间")
    utime = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


    # 关系
    user_roles = relationship("UserRole", back_populates="user", overlaps="roles,users")
    user_jobs = relationship("UserJob", back_populates="user", overlaps="jobs,users")

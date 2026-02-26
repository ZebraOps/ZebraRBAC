from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.user import User
from app.models.group import Group
from app.models.menu import Menu
from app.models.function import Function
from app.models.component import Component
from app.core.security import get_password_hash
import logging

logger = logging.getLogger(__name__)


def init_system():
    """
    系统初始化函数，包含：
    1. 初始化数据库表
    2. 创建管理员账户
    3. 创建初始数据
    """
    try:
        # 初始化数据库表
        init_db()
        logger.info("数据库表初始化成功")

        db = SessionLocal()
        try:
            # 创建管理员账户
            admin = db.query(User).filter(User.username == "admin").first()
            if not admin:
                admin = User(
                    username="admin",
                    nickname="系统管理员",
                    email="admin@example.com",
                    tel="13800000000",
                    password=get_password_hash("admin"),
                    superuser="0",  # 0表示超级用户
                    status="0",  # 0表示正常状态
                )
                db.add(admin)
                db.commit()
                logger.info("管理员账户创建成功")

            # 创建默认分组和初始数据
            default_group = db.query(Group).filter(Group.group_name == "默认组").first()
            if not default_group:
                default_group = Group(
                    group_name="默认组",
                    description="系统默认分组",
                    status="0"
                )
                db.add(default_group)
                db.commit()
                db.refresh(default_group)
                logger.info("默认分组创建成功")

                # 创建基本菜单
                if db.query(Menu).count() == 0:
                    menus = [
                        Menu(menu_name="用户管理", status="0", group_id=default_group.group_id),
                        Menu(menu_name="角色管理", status="0", group_id=default_group.group_id),
                        Menu(menu_name="权限管理", status="0", group_id=default_group.group_id)
                    ]
                    db.add_all(menus)
                    db.commit()
                    logger.info("基本菜单创建成功")

                # 创建基本功能
                if db.query(Function).count() == 0:
                    functions = [
                        Function(func_name="用户查询", func_code="user:query", status="0",
                                 group_id=default_group.group_id),
                        Function(func_name="用户创建", func_code="user:create", status="0",
                                 group_id=default_group.group_id),
                        Function(func_name="用户编辑", func_code="user:update", status="0",
                                 group_id=default_group.group_id),
                        Function(func_name="用户删除", func_code="user:delete", status="0",
                                 group_id=default_group.group_id)
                    ]
                    db.add_all(functions)
                    db.commit()
                    logger.info("基本功能创建成功")

                # 创建基本组件
                if db.query(Component).count() == 0:
                    components = [
                        Component(component_name="用户表格", status="0", group_id=default_group.group_id),
                        Component(component_name="角色选择器", status="0", group_id=default_group.group_id)
                    ]
                    db.add_all(components)
                    db.commit()
                    logger.info("基本组件创建成功")

            logger.info("系统初始化完成")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"系统初始化失败: {str(e)}")
        raise

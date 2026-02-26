from app.db.session import SessionLocal
from app.models.group import Group
from app.models.menu import Menu
from app.models.function import Function
from app.models.component import Component


def create_initial_data():
    db = SessionLocal()
    try:
        # 检查默认组是否已存在
        default_group = db.query(Group).filter(Group.group_name == "默认组").first()
        if not default_group:
            # 创建默认组
            default_group = Group(
                group_name="默认组",
                group_code="default",
                description="系统默认分组",
                status="0"
            )
            db.add(default_group)
            db.commit()
            db.refresh(default_group)
            print("默认组创建成功!")

        # 创建基本菜单
        if db.query(Menu).count() == 0:
            menus = [
                Menu(menu_name="用户管理", status="0", group_id=default_group.group_id),
                Menu(menu_name="角色管理", status="0", group_id=default_group.group_id),
                Menu(menu_name="权限管理", status="0", group_id=default_group.group_id)
            ]
            db.add_all(menus)
            db.commit()
            print("基本菜单创建成功!")

        # 创建基本功能
        if db.query(Function).count() == 0:
            functions = [
                Function(func_name="用户查询", func_code="user:query", status="0", group_id=default_group.group_id),
                Function(func_name="用户创建", func_code="user:create", status="0", group_id=default_group.group_id),
                Function(func_name="用户编辑", func_code="user:update", status="0", group_id=default_group.group_id),
                Function(func_name="用户删除", func_code="user:delete", status="0", group_id=default_group.group_id)
            ]
            db.add_all(functions)
            db.commit()
            print("基本功能创建成功!")

        # 创建基本组件
        if db.query(Component).count() == 0:
            components = [
                Component(component_name="用户表格", status="0", group_id=default_group.group_id),
                Component(component_name="角色选择器", status="0", group_id=default_group.group_id)
            ]
            db.add_all(components)
            db.commit()
            print("基本组件创建成功!")

        print("初始数据创建完成!")
    finally:
        db.close()


if __name__ == "__main__":
    create_initial_data()

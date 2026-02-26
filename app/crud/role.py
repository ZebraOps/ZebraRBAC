from typing import List, Optional, Union, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.role import Role
from app.models.user import User
from app.models.group import Group
from app.models.function import Function
from app.models.user_role import UserRole
from app.models.menu import Menu
from app.models.role_menu import RoleMenu
from app.models.component import Component
from app.models.role_component import RoleComponent
from app.models.role_function import RoleFunction
from app.schemas.role import RoleCreate, RoleUpdate


class CRUDRole:
    def get(self,
            db: Session,
            role_id: int) -> Optional[Role]:
        return db.query(Role).filter(Role.role_id == role_id).first()

    def get_by_name_and_group(self,
                              db: Session,
                              name: str,
                              group_id: int,
                              exclude_id: Optional[int] = None) -> Optional[Role]:
        query = db.query(Role).filter(Role.role_name == name, Role.group_id == group_id)
        if exclude_id:
            query = query.filter(Role.role_id != exclude_id)
        return query.first()

    def get_by_group(self,
                     db: Session,
                     group_id: int,
                     skip: int = 0,
                     limit: int = 100) -> list[type[Role]]:
        return db.query(Role).filter(Role.group_id == group_id).order_by(Role.role_id).offset(skip).limit(limit).all()

    def get_multi(self,
                  db: Session, *,
                  skip: int = 0,
                  limit: int = 100,
                  name: Optional[str] = None,
                  status: Optional[str] = None,
                  group_id: Optional[int] = None) -> Tuple[list[type[Role]], int]:
        query = db.query(Role)
        if group_id:
            query = query.filter(Role.group_id == group_id)
        if name:
            query = query.filter(Role.role_name.like(f"%{name}%"))
        if status:
            query = query.filter(Role.status == status)
        total = query.count()
        roles = query.order_by(Role.role_id).offset(skip).limit(limit).all()
        return roles, total

    def create(self,
               db: Session,
               *,
               obj_in: RoleCreate) -> Role:
        group = db.query(Group).filter(Group.group_id == obj_in.group_id).first()
        group_name = group.group_name if group else ""
        db_obj = Role(
            role_name=obj_in.role_name,
            group_id=obj_in.group_id,
            status="0",
            group=group_name,
            projects=""
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self,
               db: Session,
               *,
               db_obj: Role,
               obj_in: Union[RoleUpdate, Dict[str, Any]]) -> Role:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self,
               db: Session,
               *,
               role_id: int) -> Role:
        obj = db.query(Role).get(role_id)
        db.delete(obj)
        db.commit()
        return obj

    def has_users(self,
                  db: Session,
                  *,
                  role_id: int) -> bool:
        return db.query(UserRole).filter(UserRole.role_id == role_id).first() is not None

    def get_role_users(self,
                       db: Session,
                       role_id: int) -> List[type[User]]:
        """
        获取角色关联的用户列表
        """
        return db.query(User).join(
            UserRole, UserRole.user_id == User.user_id
        ).filter(
            UserRole.role_id == role_id,
            User.status == "0"
        ).all()

    def assign_users(self,
                     db: Session,
                     role_id: int,
                     user_ids: List[int]) -> List[type[User]]:
        """
        为角色分配用户
        """
        # 获取角色
        role = db.query(Role).filter(Role.role_id == role_id).first()
        if not role:
            raise ValueError("角色不存在")

        # 获取现有用户ID
        existing_user_ids = {
            ur.user_id for ur in db.query(UserRole).filter(
                UserRole.role_id == role_id
            ).all()
        }

        # 添加新用户
        for user_id in user_ids:
            if user_id not in existing_user_ids:
                user_role = UserRole(user_id=user_id, role_id=role_id)
                db.add(user_role)

        db.commit()
        db.refresh(role)

        return self.get_role_users(db, role_id)

    def remove_users(self,
                     db: Session,
                     role_id: int,
                     user_ids: List[int]) -> List[type[User]]:
        """
        移除角色关联的用户
        """
        # 获取角色
        role = db.query(Role).filter(Role.role_id == role_id).first()
        if not role:
            raise ValueError("角色不存在")

        # 移除指定用户
        db.query(UserRole).filter(
            UserRole.role_id == role_id,
            UserRole.user_id.in_(user_ids)
        ).delete(synchronize_session=False)

        db.commit()
        db.refresh(role)

        return self.get_role_users(db, role_id)

    def get_role_menus(self,
                       db: Session,
                       role_id: int,
                       skip: int = 0,
                       limit: int = 100) -> List[type[Menu]]:
        """
        获取角色关联的菜单列表
        """
        subquery = select(RoleMenu.menu_id).where(
            RoleMenu.role_id == role_id
        ).distinct()

        return db.query(Menu).filter(
            Menu.menu_id.in_(subquery),
            Menu.status == "0"
        ).offset(skip).limit(limit).all()

    def assign_menus(self,
                     db: Session,
                     role_id: int,
                     menu_ids: List[int]) -> List[type[Menu]]:
        """
        为角色分配菜单
        """
        # 获取角色
        role = db.query(Role).filter(Role.role_id == role_id).first()
        if not role:
            raise ValueError("角色不存在")

        # 获取现有菜单ID
        existing_menu_ids = {
            rm.menu_id for rm in db.query(RoleMenu).filter(
                RoleMenu.role_id == role_id
            ).all()
        }

        # 添加新菜单
        for menu_id in menu_ids:
            if menu_id not in existing_menu_ids:
                role_menu = RoleMenu(role_id=role_id, menu_id=menu_id)
                db.add(role_menu)

        db.commit()
        db.refresh(role)

        return self.get_role_menus(db, role_id)

    def remove_menus(self,
                     db: Session,
                     role_id: int,
                     menu_ids: List[int]) -> List[type[Menu]]:
        """
        移除角色关联的菜单
        """
        # 获取角色
        role = db.query(Role).filter(Role.role_id == role_id).first()
        if not role:
            raise ValueError("角色不存在")

        # 移除指定菜单
        db.query(RoleMenu).filter(
            RoleMenu.role_id == role_id,
            RoleMenu.menu_id.in_(menu_ids)
        ).delete(synchronize_session=False)

        db.commit()
        db.refresh(role)

        return self.get_role_menus(db, role_id)

    def get_role_components(self,
                            db: Session,
                            role_id: int) -> List[type[Component]]:
        """
        获取角色关联的组件列表
        """
        subquery = select(RoleComponent.component_id).where(
            RoleComponent.role_id == role_id
        ).distinct()

        return db.query(Component).filter(
            Component.component_id.in_(subquery),
            Component.status == "0"
        ).all()

    def assign_components(self,
                          db: Session,
                          role_id: int,
                          component_ids: List[int]) -> List[type[Component]]:
        """
        为角色分配组件
        """
        # 获取角色
        role = db.query(Role).filter(Role.role_id == role_id).first()
        if not role:
            raise ValueError("角色不存在")

        # 获取现有组件ID
        existing_component_ids = {
            rc.component_id for rc in db.query(RoleComponent).filter(
                RoleComponent.role_id == role_id
            ).all()
        }

        # 添加新组件
        for component_id in component_ids:
            if component_id not in existing_component_ids:
                role_component = RoleComponent(role_id=role_id, component_id=component_id)
                db.add(role_component)

        db.commit()
        db.refresh(role)

        return self.get_role_components(db, role_id)

    def remove_components(self,
                          db: Session,
                          role_id: int,
                          component_ids: List[int]) -> List[type[Component]]:
        """
        移除角色关联的组件
        """
        # 获取角色
        role = db.query(Role).filter(Role.role_id == role_id).first()
        if not role:
            raise ValueError("角色不存在")

        # 移除指定组件
        db.query(RoleComponent).filter(
            RoleComponent.role_id == role_id,
            RoleComponent.component_id.in_(component_ids)
        ).delete(synchronize_session=False)

        db.commit()
        db.refresh(role)

        return self.get_role_components(db, role_id)

    """
    角色授权功能
    """

    def get_role_functions(self,
                           db: Session,
                           role_id: int) -> List[type[Function]]:
        """
        获取角色关联的功能点列表
        """
        subquery = select(RoleFunction.func_id).where(
            RoleFunction.role_id == role_id
        ).distinct()

        return db.query(Function).filter(
            Function.func_id.in_(subquery),
            Function.status == "0"
        ).all()

    def assign_functions(self,
                         db: Session,
                         role_id: int,
                         function_ids: List[int]) -> List[type[Function]]:
        """
        为角色分配功能点
        """
        # 获取角色
        role = db.query(Role).filter(Role.role_id == role_id).first()
        if not role:
            raise ValueError("角色不存在")

        # 获取现有功能点ID
        existing_function_ids = {
            rf.func_id for rf in db.query(RoleFunction).filter(
                RoleFunction.role_id == role_id
            ).all()
        }

        # 添加新功能点
        for function_id in function_ids:
            if function_id not in existing_function_ids:
                role_function = RoleFunction(role_id=role_id, func_id=function_id)
                db.add(role_function)

        db.commit()
        db.refresh(role)

        return self.get_role_functions(db, role_id)

    def remove_functions(self,
                         db: Session,
                         role_id: int,
                         function_ids: List[int]) -> List[type[Function]]:
        """
        移除角色关联的功能点
        """
        # 获取角色
        role = db.query(Role).filter(Role.role_id == role_id).first()
        if not role:
            raise ValueError("角色不存在")

        # 移除指定功能点
        db.query(RoleFunction).filter(
            RoleFunction.role_id == role_id,
            RoleFunction.func_id.in_(function_ids)
        ).delete(synchronize_session=False)

        db.commit()
        db.refresh(role)

        return self.get_role_functions(db, role_id)


role = CRUDRole()

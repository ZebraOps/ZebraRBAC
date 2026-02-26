from typing import List, Optional, Union, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.crud.base import CRUDBase
from app.models.menu import Menu
from app.models.role_menu import RoleMenu
from app.schemas.menu import MenuCreate, MenuUpdate


class CRUDMenu(CRUDBase[Menu, MenuCreate, MenuUpdate]):
    def get_menu_tree(self,
                      db: Session,
                      name: Optional[str] = None,
                      status: Optional[str] = None,
                      path: Optional[str] = None) -> List[Menu]:
        """
        获取菜单树状结构，支持通过名称、状态、路径过滤
        :param db: 数据库会话
        :param name: 菜单名称，用于过滤
        :param status: 菜单状态，用于过滤
        :param path: 菜单路径，用于过滤
        :return: 菜单树列表
        """
        # 如果提供了过滤参数，需要获取所有匹配的菜单及其完整的父子关系
        if name or status or path:
            # 构建查询条件
            query = db.query(Menu)
            if name:
                query = query.filter(Menu.menu_name.like(f"%{name}%"))
            if status:
                query = query.filter(Menu.status == status)
            if path:
                query = query.filter(Menu.path.like(f"%{path}%"))

            # 先找出所有匹配条件的菜单
            matching_menus = query.all()

            # 获取这些菜单的ID
            matching_ids = [menu.menu_id for menu in matching_menus]

            # 获取这些菜单的所有祖先菜单ID
            ancestor_ids = set()
            for menu in matching_menus:
                self._get_ancestors(db, menu.menu_id, ancestor_ids)

            # 合并所有需要的菜单ID
            all_required_ids = set(matching_ids) | ancestor_ids

            # 查询所有需要的菜单
            all_menus = db.query(Menu).filter(Menu.menu_id.in_(all_required_ids)).all()

            # 构建树结构
            return self._build_menu_tree(all_menus)
        else:
            # 原始逻辑，无过滤
            query = db.query(self.model)
            # 注意：这里移除了默认的status=="0"过滤，让status参数控制过滤行为
            menus = query.order_by(self.model.order_num).all()
            return self._build_menu_tree(menus)

    def _get_ancestors(self,
                       db: Session,
                       menu_id: int,
                       ancestor_ids: set):
        """
        递归获取菜单的所有祖先菜单ID
        """
        menu = db.query(Menu).filter(Menu.menu_id == menu_id).first()
        if menu and menu.parent_id:
            ancestor_ids.add(menu.parent_id)
            self._get_ancestors(db, menu.parent_id, ancestor_ids)

    def _build_menu_tree(self,
                         menus: List[Menu]) -> List[Menu]:
        """
        构建菜单树
        """
        # 创建菜单ID到菜单对象的映射
        menu_dict = {menu.menu_id: menu for menu in menus}

        # 初始化每个菜单的children列表
        for menu in menus:
            menu.children = []

        root_menus = []
        for menu in menus:
            if menu.parent_id and menu.parent_id in menu_dict:
                # 有父节点，添加到父节点的children中
                parent_menu = menu_dict[menu.parent_id]
                parent_menu.children.append(menu)
            else:
                # 没有父节点或父节点不存在，作为根节点
                root_menus.append(menu)

        return root_menus

    def get_by_parent(self,
                      db: Session,
                      parent_id: int) -> List[Menu]:
        """
        根据父菜单ID获取子菜单
        """
        return db.query(self.model).filter(
            self.model.parent_id == parent_id,
            self.model.status == "0"
        ).order_by(self.model.order_num).all()

    def get(self,
            db: Session,
            menu_id: int) -> Optional[Menu]:
        return db.query(Menu).filter(Menu.menu_id == menu_id).first()

    def get_by_name_and_group(self,
                              db: Session,
                              name: str,
                              group_id: int,
                              exclude_id: Optional[int] = None) -> Optional[Menu]:
        query = db.query(Menu).filter(Menu.menu_name == name, Menu.group_id == group_id)
        if exclude_id:
            query = query.filter(Menu.menu_id != exclude_id)
        return query.first()

    def get_by_name(self,
                    db: Session,
                    name: str) -> Optional[Menu]:
        query = db.query(Menu).filter(Menu.menu_name == name)
        return query.first()

    def get_by_group(self,
                     db: Session,
                     group_id: int,
                     skip: int = 0,
                     limit: int = 100) -> list[type[Menu]]:
        return db.query(Menu).filter(Menu.group_id == group_id).order_by(Menu.menu_id).offset(skip).limit(limit).all()

    def get_multi(self,
                  db: Session,
                  *,
                  skip: int = 0,
                  limit: int = 100,
                  name: Optional[str] = None,
                  status: Optional[str] = None) -> Tuple[list[type[Menu]], int]:
        query = db.query(Menu)
        print(77777777)
        if name:
            query = query.filter(Menu.menu_name.ilike(f"%{name}%"))
        if status:
            query = query.filter(Menu.status == status)
        total = query.count()
        menus = query.order_by(Menu.menu_id).offset(skip).limit(limit).all()

        return menus, total

    def create(self,
               db: Session,
               *,
               obj_in: MenuCreate) -> Menu:
        db_obj = Menu(
            menu_name=obj_in.menu_name,
            status="0",
            parent_id=obj_in.parent_id,
            order_num=obj_in.order_num,
            icon=obj_in.icon,
            path=obj_in.path,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self,
               db: Session,
               *,
               db_obj: Menu,
               obj_in: Union[MenuUpdate, Dict[str, Any]]) -> Menu:
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
               menu_id: int) -> Menu:
        obj = db.query(Menu).get(menu_id)
        db.delete(obj)
        db.commit()
        return obj

    def has_roles(self,
                  db: Session,
                  *,
                  menu_id: int) -> bool:
        return db.query(RoleMenu).filter(RoleMenu.menu_id == menu_id).first() is not None

    def get_menus_by_roles(self,
                           db: Session,
                           role_ids: List[int]) -> List[Menu]:
        """
        根据角色ID列表获取菜单列表
        """
        return db.query(self.model).join(
            RoleMenu, RoleMenu.menu_id == self.model.menu_id
        ).filter(
            RoleMenu.role_id.in_(role_ids),
            self.model.status == "0"
        ).order_by(self.model.order_num).all()


menu = CRUDMenu(Menu)

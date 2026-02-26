from typing import List, Optional, Union, Dict, Any, Tuple
from sqlalchemy.orm import Session

from app.models.component import Component
from app.models.role_component import RoleComponent
from app.schemas.component import ComponentCreate, ComponentUpdate


class CRUDComponent:
    def get(self,
            db: Session,
            component_id: int) -> Optional[Component]:
        return db.query(Component).filter(Component.component_id == component_id).first()

    def get_by_name_and_group(self,
                              db: Session,
                              name: str,
                              group_id: int,
                              exclude_id: Optional[int] = None) -> Optional[Component]:
        query = db.query(Component).filter(Component.component_name == name, Component.group_id == group_id)
        if exclude_id:
            query = query.filter(Component.component_id != exclude_id)
        return query.first()

    def get_by_group(self,
                     db: Session,
                     group_id: int,
                     skip: int = 0,
                     limit: int = 100) -> List[type[Component]]:
        return db.query(Component).filter(Component.group_id == group_id).order_by(Component.component_id).offset(
            skip).limit(limit).all()

    def get_multi(self,
                  db: Session, *,
                  skip: int = 0,
                  limit: int = 100,
                  name: Optional[str] = None,
                  status: Optional[str] = None) -> Tuple[list[type[Component]], int]:
        query = db.query(Component)
        if name:
            query = query.filter(Component.component_name.ilike(f"%{name}%"))
        if status:
            query = query.filter(Component.status == status)
        total = query.count()
        comp = query.order_by(Component.component_id).offset(skip).limit(limit).all()
        return comp, total

    def create(self,
               db: Session,
               *,
               obj_in: ComponentCreate) -> Component:
        db_obj = Component(
            component_name=obj_in.component_name,
            group_id=obj_in.group_id,
            status="0",
            group=""  # 兼容旧数据
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self,
               db: Session,
               *,
               db_obj: Component,
               obj_in: Union[ComponentUpdate, Dict[str, Any]]) -> Component:
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
               component_id: int) -> Component:
        obj = db.query(Component).get(component_id)
        db.delete(obj)
        db.commit()
        return obj

    def has_roles(self,
                  db: Session,
                  *,
                  component_id: int) -> bool:
        return db.query(RoleComponent).filter(RoleComponent.component_id == component_id).first() is not None

    def get_components_by_roles(self,
                                db: Session,
                                role_ids: List[int]) -> List[type[Component]]:
        """
        根据角色ID列表获取组件列表
        """
        return db.query(Component).join(
            RoleComponent, RoleComponent.component_id == Component.component_id
        ).filter(
            RoleComponent.role_id.in_(role_ids),
            Component.status == "0"
        ).all()


component = CRUDComponent()

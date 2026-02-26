from typing import List, Optional, Any, Tuple
from sqlalchemy.orm import Session

from app.models.group import Group
from app.schemas.group import GroupCreate, GroupUpdate


class CRUDGroup:
    def get(self,
            db: Session,
            group_id: int) -> Optional[Group]:
        return db.query(Group).filter(Group.group_id == group_id).first()

    def get_by_name(self,
                    db: Session,
                    name: str) -> Optional[Group]:
        return db.query(Group).filter(Group.group_name == name).first()

    def get_by_code(self,
                    db: Session,
                    code: str) -> Optional[Group]:
        return db.query(Group).filter(Group.group_code == code).first()

    def get_multi(self,
                  db: Session, *,
                  skip: int = 0,
                  limit: int = 100,
                  name: Optional[str] = None,
                  status: Optional[str] = None) -> Tuple[list[type[Group]], int]:
        query = db.query(Group)
        if name:
            query = query.filter(Group.group_name.ilike(f"%{name}%"))
        if status:
            query = query.filter(Group.status == status)
        total = query.count()
        groups = query.order_by(Group.group_id).offset(skip).limit(limit).all()
        return groups, total

    def create(self,
               db: Session,
               *,
               obj_in: GroupCreate) -> Group:
        db_obj = Group(
            group_name=obj_in.group_name,
            status=obj_in.status,
            description=obj_in.description
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self,
               db: Session,
               *,
               db_obj: Group,
               obj_in: GroupUpdate) -> Group:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self,
               db: Session,
               *,
               group_id: int) -> Group:
        obj = db.query(Group).get(group_id)
        db.delete(obj)
        db.commit()
        return obj


group = CRUDGroup()

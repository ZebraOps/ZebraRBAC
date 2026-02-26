from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.user_organization import UserOrganization
from app.models.user import User
from app.models.organization import Organization
from app.models.position import Position
from app.schemas.user_organization import UserOrganizationCreate


class CRUDUserOrganization:
    def get(self,
            db: Session,
            id: int) -> Optional[UserOrganization]:
        return db.query(UserOrganization).filter(UserOrganization.id == id).first()

    def get_by_user(self,
                    db: Session,
                    user_id: int) -> List[UserOrganization]:
        return db.query(UserOrganization).filter(UserOrganization.user_id == user_id).all()

    def get_by_org(self,
                   db: Session,
                   org_id: int) -> List[UserOrganization]:
        return db.query(UserOrganization).filter(UserOrganization.org_id == org_id).all()

    def create(self,
               db: Session,
               *,
               obj_in: UserOrganizationCreate) -> UserOrganization:
        db_obj = UserOrganization(
            user_id=obj_in.user_id,
            org_id=obj_in.org_id,
            position_id=obj_in.position_id,
            is_primary=obj_in.is_primary
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self,
               db: Session,
               *,
               id: int) -> UserOrganization:
        obj = db.query(UserOrganization).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def set_primary(self,
                    db: Session,
                    user_id: int,
                    org_id: int,
                    position_id: int) -> UserOrganization:
        # 将用户在其他组织职务的主岗设置为非主岗
        db.query(UserOrganization).filter(
            UserOrganization.user_id == user_id
        ).update({UserOrganization.is_primary: 0})

        # 设置新的主岗
        obj = db.query(UserOrganization).filter(
            UserOrganization.user_id == user_id,
            UserOrganization.org_id == org_id,
            UserOrganization.position_id == position_id
        ).first()

        if obj:
            obj.is_primary = 1
            db.add(obj)
            db.commit()
            db.refresh(obj)

        return obj


user_organization = CRUDUserOrganization()

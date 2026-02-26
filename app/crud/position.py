from typing import List, Optional, Union, Dict, Any
from sqlalchemy.orm import Session

from app.models.position import Position
from app.schemas.position import PositionCreate, PositionUpdate


class CRUDPosition:
    def get(self,
            db: Session,
            position_id: int) -> Optional[Position]:
        return db.query(Position).filter(Position.position_id == position_id).first()

    def get_by_code(self,
                    db: Session,
                    code: str) -> Optional[Position]:
        return db.query(Position).filter(Position.position_code == code).first()

    def get_multi(self,
                  db: Session, *,
                  skip: int = 0,
                  limit: int = 100,
                  position_name: Optional[str] = None,
                  position_code: Optional[str] = None) -> List[Position]:
        query = db.query(Position)
        if position_name:
            query = query.filter(Position.position_name.ilike(f"%{position_name}%"))

        if position_code:
            query = query.filter(Position.position_code.ilike(f"%{position_code}%"))

        total = query.count()
        positions = query.order_by(Position.position_id).offset(skip).limit(limit).all()

        return positions, total

    def create(self,
               db: Session,
               *,
               obj_in: PositionCreate) -> Position:
        db_obj = Position(
            position_name=obj_in.position_name,
            description=obj_in.description
        )
        db.add(db_obj)
        db.flush()

        db_obj.position_code = f"POS-{db_obj.position_id:02d}"
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self,
            db: Session,
            *,
            db_obj: Position,
            obj_in: Union[PositionUpdate, Dict[str, Any]]) -> Position:
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
               position_id: int) -> Position:
        obj = db.query(Position).get(position_id)
        db.delete(obj)
        db.commit()
        return obj


position = CRUDPosition()

from typing import List, Optional, Union, Dict, Any, Tuple
from sqlalchemy.orm import Session

from app.models.function import Function
from app.models.role import Role
from app.models.role_function import RoleFunction
from app.schemas.function import FunctionCreate, FunctionUpdate


class CRUDFunction:
    def get(self,
            db: Session,
            func_id: int) -> Optional[Function]:
        return db.query(Function).filter(Function.func_id == func_id).first()

    def get_by_name_and_group(self,
                              db: Session,
                              name: str,
                              group_id: int,
                              exclude_id: Optional[int] = None) -> Optional[Function]:
        query = db.query(Function).filter(Function.func_name == name, Function.group_id == group_id)
        if exclude_id:
            query = query.filter(Function.func_id != exclude_id)
        return query.first()

    def get_by_uri_and_method(self,
                              db: Session,
                              uri: str,
                              method_type: str,
                              exclude_id: Optional[int] = None) -> Optional[Function]:
        query = db.query(Function).filter(Function.uri == uri, Function.method_type == method_type)
        if exclude_id:
            query = query.filter(Function.func_id != exclude_id)
        return query.first()

    def get_by_group(self,
                     db: Session,
                     group_id: int,
                     skip: int = 0,
                     limit: int = 100) -> list[type[Function]]:
        return db.query(Function).filter(Function.group_id == group_id).order_by(Function.func_id).offset(skip).limit(
            limit).all()

    def get_multi(self, db: Session, *,
                  skip: int = 0,
                  limit: int = 100,
                  name: Optional[str] = None,
                  status: Optional[str] = None,
                  uri: Optional[str] = None,
                  group_id: Optional[int] = None) -> Tuple[list[type[Role]], int]:
        query = db.query(Function)
        if group_id:
            query = query.filter(Function.group_id == group_id)
        if name:
            query = query.filter(Function.func_name.like(f"%{name}%"))
        if status:
            query = query.filter(Function.status == status)
        if uri:
            query = query.filter(Function.uri.like(f"%{uri}%"))
        total = query.count()
        functions = query.order_by(Function.func_id).offset(skip).limit(limit).all()
        return functions, total

    def create(self,
               db: Session,
               *,
               obj_in: FunctionCreate) -> Function:
        db_obj = Function(
            func_name=obj_in.func_name,
            uri=obj_in.uri,
            method_type=obj_in.method_type.upper(),
            group_id=obj_in.group_id,
            status=obj_in.status,
            group=obj_in.group
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self,
               db: Session,
               *,
               db_obj: Function,
               obj_in: Union[FunctionUpdate, Dict[str, Any]]) -> Function:
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
               func_id: int) -> Function:
        obj = db.query(Function).get(func_id)
        db.delete(obj)
        db.commit()
        return obj

    def has_roles(self,
                  db: Session,
                  *,
                  func_id: int) -> bool:
        return db.query(RoleFunction).filter(RoleFunction.func_id == func_id).first() is not None

    def get_functions_by_roles(self,
                               db: Session,
                               role_ids: List[int]) -> List[type[Function]]:
        """
        根据角色ID获取功能点列表
        """
        if not role_ids:
            return []

        # 查询功能点
        query = db.query(Function).join(
            RoleFunction, RoleFunction.func_id == Function.func_id
        ).filter(
            RoleFunction.role_id.in_(role_ids), Function.status == "0"
        )

        result = query.all()
        return result


function = CRUDFunction()

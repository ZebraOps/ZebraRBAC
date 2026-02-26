from typing import List, Optional, Union, Dict, Any
from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate, OrganizationUpdate


class CRUDOrganization:
    def get(self,
            db: Session,
            org_id: int) -> Optional[Organization]:
        return db.query(Organization).filter(Organization.org_id == org_id).first()

    def get_by_code(self,
                    db: Session,
                    code: str) -> Optional[Organization]:
        return db.query(Organization).filter(Organization.org_code == code).first()

    def get_multi(self,
                  db: Session,
                  *,
                  skip: int = 0,
                  limit: int = 100) -> List[Organization]:
        return db.query(Organization).offset(skip).limit(limit).all()

    def get_org_tree(self,
                     db: Session,
                     parent_id: Optional[int] = None,
                     name: Optional[str] = None) -> List[Organization]:
        """
        获取组织树结构（优化版本，避免递归查询）
        :param db: 数据库会话
        :param parent_id: 父级组织ID
        :param name: 组织名称，用于过滤
        :return: 组织树列表
        """
        # 如果提供了name参数，需要获取所有匹配的组织及其完整的父子关系
        if name:
            # 先找出所有匹配名称的组织
            matching_orgs = db.query(Organization).filter(
                Organization.org_name.like(f"%{name}%")
            ).all()

            # 获取这些组织的ID
            matching_ids = [org.org_id for org in matching_orgs]

            # 获取这些组织的所有祖先组织ID
            ancestor_ids = set()
            for org in matching_orgs:
                self._get_ancestors(db, org.org_id, ancestor_ids)

            # 合并所有需要的组织ID
            all_required_ids = set(matching_ids) | ancestor_ids

            # 查询所有需要的组织
            query = db.query(Organization).filter(Organization.org_id.in_(all_required_ids))
            if parent_id is None:
                all_orgs = query.filter(Organization.parent_id.is_(None)).order_by(Organization.order_num).all()
            else:
                all_orgs = query.filter(Organization.parent_id == parent_id).order_by(Organization.order_num).all()

            # 构建树结构
            for org in all_orgs:
                org_children = self._build_filtered_tree(db, org.org_id, all_required_ids)
                # 只有当有子节点时才设置children属性
                if org_children:
                    org.children = org_children
            return all_orgs
        else:
            # 原始逻辑，无过滤
            query = db.query(Organization)

            if parent_id is None:
                orgs = query.filter(
                    Organization.parent_id.is_(None)
                ).order_by(Organization.order_num).all()
            else:
                orgs = query.filter(
                    Organization.parent_id == parent_id
                ).order_by(Organization.order_num).all()

            # 为每个组织递归获取子组织
            for org in orgs:
                org_id = org.org_id
                if org_id is not None:
                    org_children = self.get_org_tree(db, org_id)
                    # 只有当有子节点时才设置children属性
                    if org_children:
                        org.children = org_children
            return orgs

    def _get_ancestors(self,
                       db: Session,
                       org_id: int,
                       ancestor_ids: set):
        """
        递归获取组织的所有祖先组织ID
        """
        org = db.query(Organization).filter(Organization.org_id == org_id).first()
        if org and org.parent_id:
            ancestor_ids.add(org.parent_id)
            self._get_ancestors(db, org.parent_id, ancestor_ids)

    def _build_filtered_tree(self,
                             db: Session,
                             parent_id: int,
                             allowed_ids: set) -> List[Organization]:
        """
        构建过滤后的组织树
        """
        children = db.query(Organization).filter(
            Organization.parent_id == parent_id
        ).order_by(Organization.order_num).all()

        result = []
        for child in children:
            if child.org_id in allowed_ids:
                # 递归构建子树
                child_children = self._build_filtered_tree(db, child.org_id, allowed_ids)

                # 只有当有子节点时才设置children属性
                if child_children:
                    child.children = child_children
                result.append(child)

        return result

    def create(self,
               db: Session,
               *,
               obj_in: OrganizationCreate) -> Organization:
        db_obj = Organization(
            org_name=obj_in.org_name,
            org_code=obj_in.org_code,
            parent_id=obj_in.parent_id,
            level=obj_in.level if obj_in.level else 0,
            order_num=obj_in.order_num
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self,
        db: Session,
        *,
        db_obj: Organization,
        obj_in: Union[OrganizationUpdate, Dict[str, Any]]) -> Organization:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            # 处理 Pydantic 模型
            update_data = obj_in.dict(exclude_unset=True)

        # 特别处理 parent_id 字段
        if 'parent_id' in update_data:
            # 将 0 转换为 None
            if update_data['parent_id'] == 0:
                update_data['parent_id'] = None

        for field in update_data:
            if field != "org_id":  # 避免更新主键
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self,
               db: Session,
               *,
               org_id: int) -> Organization:
        obj = db.query(Organization).get(org_id)
        db.delete(obj)
        db.commit()
        return obj


organization = CRUDOrganization()

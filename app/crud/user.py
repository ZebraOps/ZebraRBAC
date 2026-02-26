from typing import List, Optional, Dict, Any, Union

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy import Integer

from app.core.security import get_password_hash, verify_password
from app.models.role import Role
from app.models.user import User
from app.models.user_role import UserRole
from app.models.user_job import UserJob
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser:
    def get(self,
            db: Session,
            user_id: int) -> Optional[User]:
        return db.query(User).filter(User.user_id == user_id).first()

    def get_by_email(self,
                     db: Session,
                     email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_by_username(self,
                        db: Session,
                        username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    def get_multi(self, db: Session, *,
                  skip: int = 0,
                  limit: int = 100,
                  status: Optional[str] = "") -> tuple[List[User], int]:
        query = db.query(User)
        if status != "all":
            query = query.filter()
        total = query.count()
        users = query.offset(skip).limit(limit).all()
        for user in users:
            user.role_ids = [user_role.role_id for user_role in user.user_roles]
            user.job_ids = [user_role.job_id for user_role in user.user_jobs]


        return users, total

    def search(self,
                db: Session,
                *,
                key: Optional[str] = None,
                value: Optional[str] = None,
                username: Optional[str] = None,
                nickname: Optional[str] = None,
                skip: int = 0,
                limit: int = 100,
                status: str = "0") -> tuple[List[User], int]:
        query = db.query(User)
        if status != "all":
            query = query.filter(User.status == status)

        # 处理 key/value 搜索
        if key and value and hasattr(User, key):
            query = query.filter(getattr(User, key).like(f"%{value}%"))
        if username:
            query = query.filter(User.username.ilike(f"%{username}%"))
        if nickname:
            query = query.filter(User.nickname.ilike(f"%{nickname}%"))

        total = query.count()
        users = query.offset(skip).limit(limit).all()
        for user in users:
            user.role_ids = [user_role.role_id for user_role in user.user_roles]
            user.job_ids = [user_role.job_id for user_role in user.user_jobs]

        return users, total

    def create(self,
               db: Session,
               *,
               obj_in: UserCreate) -> User:
        # 查询当前最大工号
        max_user = db.query(User).filter(User.employee_id.isnot(None)).order_by(
            User.employee_id.cast(Integer).desc()).first()
        if max_user and max_user.employee_id:
            try:
                next_num = int(max_user.employee_id) + 1
            except ValueError:
                next_num = 1
        else:
            next_num = 1

        # 格式化工号：小于1000时补前导0，大于等于1000时不补前导0
        if next_num < 1000:
            employee_id = f"{next_num:03d}"
        else:
            employee_id = str(next_num)

        db_obj = User(
            username=obj_in.username,
            nickname=obj_in.nickname,
            email=obj_in.email,
            employee_id=employee_id,
            tel=obj_in.tel,
            wechat=obj_in.wechat,
            department=obj_in.department,
            password=get_password_hash(obj_in.password) if obj_in.password else get_password_hash("password"),
            status="0",
            gender=obj_in.gender,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        # 如果传入了角色ID，则为用户分配角色
        if hasattr(obj_in, 'role_ids') and obj_in.role_ids:
            for role_id in obj_in.role_ids:
                user_role = UserRole(user_id=db_obj.user_id, role_id=role_id)
                db.add(user_role)
            db.commit()
            db.refresh(db_obj)

        # 如果传入了岗位ID，则为用户分配岗位
        if hasattr(obj_in, 'job_ids') and obj_in.job_ids:
            for job_id in obj_in.job_ids:
                user_job = UserJob(user_id=db_obj.user_id, job_id=job_id)
                db.add(user_job)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def update(self,
               db: Session,
               *,
               db_obj: User,
               obj_in: Union[UserUpdate, Dict[str, Any]]) -> User:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        # 处理密码字段，如果存在则进行哈希处理
        if "password" in update_data and update_data["password"]:
            update_data["password"] = get_password_hash(update_data["password"])
        elif "password" in update_data:
            # 如果密码为空则移除该字段，避免覆盖原密码
            update_data.pop("password", None)

        if "status" in update_data and update_data["status"] == "0":
            db_obj.disable_at = None

        # 处理角色更新 - 增量更新方式
        if "role_ids" in update_data:
            new_role_ids = set(update_data.pop("role_ids", []))
            # 获取当前用户的角色ID集合
            current_role_ids = {user_role.role_id for user_role in db_obj.user_roles}

            # 计算需要添加和删除的角色
            roles_to_add = new_role_ids - current_role_ids
            roles_to_remove = current_role_ids - new_role_ids

            # 删除不再需要的角色
            if roles_to_remove:
                db.query(UserRole).filter(
                    UserRole.user_id == db_obj.user_id,
                    UserRole.role_id.in_(roles_to_remove)
                ).delete(synchronize_session=False)

            # 添加新的角色
            for role_id in roles_to_add:
                if role_id:
                    user_role = UserRole(user_id=db_obj.user_id, role_id=role_id)
                    db.add(user_role)

        # 处理岗位更新 - 增量更新方式
        if "job_ids" in update_data:
            new_job_ids = set(update_data.pop("job_ids", []))
            # 获取当前用户的岗位ID集合
            current_job_ids = {user_job.job_id for user_job in db_obj.user_jobs}

            # 如果 new_job_ids 为空，则删除所有岗位关联
            if not new_job_ids:
                db.query(UserJob).filter(UserJob.user_id == db_obj.user_id).delete(synchronize_session=False)
            else:
                # 计算需要添加和删除的岗位
                job_to_add = new_job_ids - current_job_ids
                job_to_remove = current_job_ids - new_job_ids

                # 删除不再需要的岗位
                if job_to_remove:
                    db.query(UserJob).filter(
                        UserJob.user_id == db_obj.user_id,
                        UserJob.job_id.in_(job_to_remove)
                    ).delete(synchronize_session=False)

                # 添加新的岗位
                for job_id in job_to_add:
                    if job_id:
                        user_job = UserJob(user_id=db_obj.user_id, job_id=job_id)
                        db.add(user_job)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_password(self,
                        db: Session,
                        *,
                        user_id: int,
                        password: str) -> User:
        db_obj = self.get(db, user_id=user_id)
        hashed_password = get_password_hash(password)
        db_obj.password = hashed_password
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self,
                     db: Session,
                     *,
                     username: str,
                     password: str) -> Optional[User]:
        user = self.get_by_username(db, username=username)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user

    def is_active(self,
                  user: User) -> bool:
        return user.status == "0"

    def is_superuser(self,
                     user: User) -> bool:
        return user.superuser == "0"

    def remove(self,
               db: Session,
               *,
               user_id: int) -> User:
        user = self.get(db, user_id=user_id)
        db.delete(user)
        db.commit()
        return user

    def get_user_roles(self,
                       db: Session,
                       user_id: int) ->  List[Role]:
        """
        获取用户的角色列表
        """
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return []
        # 通过 UserRole 中间表获取角色
        return [user_role.role for user_role in user.user_roles if user_role.role.status == "0"]

    def assign_roles(self,
                     db: Session,
                     user_id: int,
                     role_ids: List[int]) -> List[Role]:
        """
        为用户分配角色
        """
        # 获取用户
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise ValueError("用户不存在")

        # 获取现有角色ID
        existing_role_ids = {ur.role_id for ur in user.user_roles}

        # 添加新角色
        for role_id in role_ids:
            if role_id not in existing_role_ids:
                user_role = UserRole(user_id=user_id, role_id=role_id)
                db.add(user_role)

        db.commit()
        db.refresh(user)

        return self.get_user_roles(db, user_id)

    def remove_roles(self,
                     db: Session,
                     user_id: int,
                     role_ids: List[int]) -> List[Role]:
        """
        移除用户的角色
        """
        # 获取用户
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise ValueError("用户不存在")

        # 移除指定角色
        db.query(UserRole).filter(
            UserRole.user_id == user_id,
            UserRole.role_id.in_(role_ids)
        ).delete(synchronize_session=False)

        db.commit()
        db.refresh(user)

        return self.get_user_roles(db, user_id)

    def update_roles(self,
                     db: Session,
                     user_id: int,
                     role_ids: List[int]) -> List[Role]:
        """
        更新用户角色（替换现有角色）
        """
        # 获取用户
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise ValueError("用户不存在")

        # 删除现有角色关系
        db.query(UserRole).filter(UserRole.user_id == user_id).delete()

        # 添加新角色关系
        for role_id in role_ids:
            user_role = UserRole(user_id=user_id, role_id=role_id)
            db.add(user_role)

        db.commit()
        db.refresh(user)

        return self.get_user_roles(db, user_id)


user = CRUDUser()

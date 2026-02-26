# app/crud/job.py
from typing import List, Optional, Union, Dict, Any
from sqlalchemy.orm import Session

from app.models.job import Job
from app.models.user import User
from app.models.user_job import UserJob
from app.schemas.job import JobCreate, JobUpdate


class CRUDJob:
    def get(self,
            db: Session,
            job_id: int) -> Optional[Job]:
        return db.query(Job).filter(Job.job_id == job_id).first()

    def get_by_code(self,
                    db: Session,
                    code: str,
                    exclude_id: Optional[int] = None) -> Optional[Job]:
        query = db.query(Job).filter(Job.job_code == code)
        if exclude_id:
            query = query.filter(Job.job_id != exclude_id)
        return query.first()

    def get_by_name(self,
                    db: Session,
                    name: str) -> Optional[Job]:
        return db.query(Job).filter(Job.job_name == name).first()

    def get_multi(self, db: Session, *,
                  skip: int = 0,
                  limit: int = 100,
                  job_name: Optional[str] = None,
                  job_code: Optional[str] = None) -> List[Job]:
        query = db.query(Job)
        if job_name:
            query = query.filter(Job.job_name.ilike(f"%{job_name}%"))

        if job_code:
            query = query.filter(Job.job_code.ilike(f"%{job_code}%"))

        total = query.count()
        jobs = query.order_by(Job.job_id).offset(skip).limit(limit).all()

        return jobs, total

    def create(self,
               db: Session,
               *,
               obj_in: JobCreate) -> Job:
        db_obj = Job(
            job_name=obj_in.job_name,
            description=obj_in.description
        )
        db.add(db_obj)
        db.flush()

        db_obj.job_code = f"JOB-{db_obj.job_id:02d}"
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self,
               db: Session, *,
               db_obj: Job,
               obj_in: Union[JobUpdate, Dict[str, Any]]) -> Job:
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
               job_id: int) -> Job:
        obj = db.query(Job).get(job_id)
        # 检查是否有用户关联
        user_count = db.query(UserJob).filter(UserJob.job_id == job_id).count()
        if user_count > 0:
            raise ValueError("有用户关联此岗位，不能删除")
        db.delete(obj)
        db.commit()
        return obj

    def assign_user(self,
                    db: Session,
                    job_id: int,
                    user_id: int) -> User:
        """
        为用户分配岗位
        """
        job = db.query(Job).filter(Job.job_id == job_id).first()
        if not job:
            raise ValueError("岗位不存在")

        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise ValueError("用户不存在")

        user.job_id = job_id
        db.commit()
        db.refresh(user)
        return user

    def remove_user(self,
                    db: Session,
                    user_id: int) -> User:
        """
        移除用户的岗位
        """
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise ValueError("用户不存在")

        user.job_id = None
        db.commit()
        db.refresh(user)
        return user

    def get_job_users(self,
                      db: Session,
                      job_id: int,
                      skip: int = 0,
                      limit: int = 100) -> List[User]:
        """
        获取岗位关联的用户列表
        """
        return db.query(User).filter(
            User.job_id == job_id
        ).offset(skip).limit(limit).all()


job = CRUDJob()

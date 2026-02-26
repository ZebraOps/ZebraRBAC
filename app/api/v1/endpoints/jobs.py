# app/api/v1/endpoints/jobs.py
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.schemas.response import ResponseModel as Response, PageResponseModel, PageData
from app.api.dependencies import get_current_active_user, get_current_active_superuser
from app.db.session import get_db

router = APIRouter()


@router.get("", response_model=PageResponseModel[schemas.Job])
def read_jobs(
    db: Session = Depends(get_db),
    name: Optional[str] = None,
    code: Optional[str] = None,
    current: int = 0,
    size: int = 100,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    获取岗位列表
    """
    jobs, total = crud.job.get_multi(db, skip=current, limit=size, job_name=name, job_code=code)
    page_data = PageData(
        total=total,
        records=jobs
    )
    return Response(data=page_data, message="获取岗位列表成功")


@router.post("", response_model=Response[schemas.Job])
def create_job(
    *,
    db: Session = Depends(get_db),
    job_in: schemas.JobCreate,
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    创建新岗位
    """
    job = crud.job.create(db, obj_in=job_in)
    return Response(data=job, message="创建岗位成功")


@router.get("/{job_id}", response_model=Response[schemas.Job])
def read_job(
    *,
    db: Session = Depends(get_db),
    job_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    获取岗位详情
    """
    job = crud.job.get(db, job_id=job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail="岗位不存在"
        )
    return Response(data=job, message="获取岗位详情成功")


@router.put("/{job_id}", response_model=Response[schemas.Job])
def update_job(
    *,
    db: Session = Depends(get_db),
    job_id: int,
    job_in: schemas.JobUpdate,
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    更新岗位
    """
    job = crud.job.get(db, job_id=job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail="岗位不存在"
        )

    job = crud.job.update(db, db_obj=job, obj_in=job_in)
    return Response(data=job, message="更新岗位成功")


@router.delete("/{job_id}", response_model=Response[schemas.Job])
def delete_job(
    *,
    db: Session = Depends(get_db),
    job_id: int,
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    删除岗位
    """
    job = crud.job.get(db, job_id=job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail="岗位不存在"
        )

    try:
        job = crud.job.remove(db, job_id=job_id)
        return Response(data=job, message="删除岗位成功")
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.post("/{job_id}/users/{user_id}", response_model=Response[schemas.User])
def assign_user_to_job(
    *,
    db: Session = Depends(get_db),
    job_id: int,
    user_id: int,
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    为用户分配岗位
    """
    # 检查岗位是否存在
    job = crud.job.get(db, job_id=job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail="岗位不存在"
        )

    # 检查用户是否存在
    user = crud.user.get(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )

    # 为用户分配岗位
    updated_user = crud.job.assign_user(db, job_id=job_id, user_id=user_id)
    return Response(data=updated_user, message="岗位分配成功")


@router.delete("/users/{user_id}", response_model=Response[schemas.User])
def remove_user_from_job(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    移除用户的岗位
    """
    # 检查用户是否存在
    user = crud.user.get(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )

    # 移除用户的岗位
    updated_user = crud.job.remove_user(db, user_id=user_id)
    return Response(data=updated_user, message="岗位移除成功")


@router.get("/{job_id}/users", response_model=Response[List[schemas.User]])
def get_job_users(
    *,
    db: Session = Depends(get_db),
    job_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    获取岗位关联的用户列表
    """
    # 检查岗位是否存在
    job = crud.job.get(db, job_id=job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail="岗位不存在"
        )

    # 获取岗位关联的用户
    users = crud.job.get_job_users(db, job_id=job_id, skip=skip, limit=limit)
    return Response(data=users, message="获取岗位用户列表成功")

from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.schemas.response import ResponseModel as Response, PageResponseModel, PageData
from app.api.dependencies import get_current_active_user, get_current_active_superuser
from app.db.session import get_db

router = APIRouter()


@router.get("", response_model=PageResponseModel[schemas.User])
def read_users(
        db: Session = Depends(get_db),
        username: Optional[str] = Query(None),
        nickname: Optional[str] = Query(None),
        current: int = 0,
        size: int = 100,
        status: Optional[str] = "0",
        key: Optional[str] = None,
        value: Optional[str] = None,
        is_all: bool = Query(False, alias="isAll"),
        current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    获取用户列表
    """
    if (key and value) or username or nickname:
        users, total = crud.user.search(db,
                                        key=key,
                                        value=value,
                                        skip=current,
                                        limit=size,
                                        status=status,
                                        username=username,
                                        nickname=nickname
                                        )
    else:
        if is_all:
            users, total = crud.user.get_multi(db, skip=0, limit=None, status=status)
        else:
            users, total = crud.user.get_multi(db, skip=current, limit=size, status=status)

    page_data = PageData(
        total=total,
        records=users
    )
    return PageResponseModel(data=page_data, message="获取用户列表成功")


@router.post("", response_model=Response[schemas.User])
def create_user(
        *,
        db: Session = Depends(get_db),
        user_in: schemas.UserCreate,
        current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    创建新用户
    """
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="此邮箱已被注册",
        )
    user = crud.user.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail="此用户名已被使用",
        )
    user = crud.user.create(db, obj_in=user_in)
    return Response(data=user, message="用户创建成功")


@router.get("/{user_id}", response_model=schemas.User)
def read_user(
        *,
        db: Session = Depends(get_db),
        user_id: int,
        current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    获取用户详情
    """
    user = crud.user.get(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )
    return Response(data=user, message="获取用户成功")


@router.put("/{user_id}")
def update_user(
        *,
        db: Session = Depends(get_db),
        user_id: int,
        user_in: schemas.UserUpdate,
        current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    更新用户信息
    """
    user = crud.user.get(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )
    crud.user.update(db, db_obj=user, obj_in=user_in)
    return Response(message="更新用户成功")


@router.delete("/{user_id}")
def delete_user(
        *,
        db: Session = Depends(get_db),
        user_id: int,
        current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    删除用户
    """
    user = crud.user.get(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )
    if user.username == "admin":
        raise HTTPException(
            status_code=400,
            detail="不能删除管理员用户"
        )
    crud.user.remove(db, user_id=user_id)
    return Response(message="删除用户成功")


@router.post("/{user_id}/roles", response_model=Response[List[schemas.Role]])
def assign_roles_to_user(
        *,
        db: Session = Depends(get_db),
        user_id: int,
        role_ids: List[int],
        current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    为用户分配角色
    """
    # 检查用户是否存在
    user = crud.user.get(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )

    # 检查角色是否存在
    for role_id in role_ids:
        role = crud.role.get(db, role_id=role_id)
        if not role:
            raise HTTPException(
                status_code=404,
                detail=f"角色ID {role_id} 不存在"
            )

    # 分配角色给用户
    assigned_roles = crud.user.assign_roles(db, user_id=user_id, role_ids=role_ids)

    return Response(data=assigned_roles, message="角色分配成功")


@router.get("/{user_id}/roles", response_model=Response[List[schemas.Role]])
def get_user_roles(
        *,
        db: Session = Depends(get_db),
        user_id: int,
        current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    获取用户的角色列表
    """
    # 检查用户是否存在
    user = crud.user.get(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )

    # 获取用户角色
    user_roles = crud.user.get_user_roles(db, user_id=user_id)

    return Response(data=user_roles, message="获取用户角色成功")


@router.delete("/{user_id}/roles", response_model=Response[List[schemas.Role]])
def remove_user_roles(
        *,
        db: Session = Depends(get_db),
        user_id: int,
        role_ids: List[int],
        current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    移除用户的角色
    """
    # 检查用户是否存在
    user = crud.user.get(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )

    # 检查角色是否存在
    for role_id in role_ids:
        role = crud.role.get(db, role_id=role_id)
        if not role:
            raise HTTPException(
                status_code=404,
                detail=f"角色ID {role_id} 不存在"
            )

    # 移除用户角色
    remaining_roles = crud.user.remove_roles(db, user_id=user_id, role_ids=role_ids)

    return Response(data=remaining_roles, message="角色移除成功")


@router.put("/{user_id}/roles", response_model=Response[List[schemas.Role]])
def update_user_roles(
        *,
        db: Session = Depends(get_db),
        user_id: int,
        role_ids: List[int],
        current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    更新用户角色（替换现有角色）
    """
    # 检查用户是否存在
    user = crud.user.get(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )

    # 检查角色是否存在
    for role_id in role_ids:
        role = crud.role.get(db, role_id=role_id)
        if not role:
            raise HTTPException(
                status_code=404,
                detail=f"角色ID {role_id} 不存在"
            )

    # 更新用户角色
    updated_roles = crud.user.update_roles(db, user_id=user_id, role_ids=role_ids)

    return Response(data=updated_roles, message="用户角色更新成功")


# app/api/v1/endpoints/users.py
# 在适当位置添加以下接口

@router.get("/{user_id}/job", response_model=Response[schemas.Job])
def get_user_job(
        *,
        db: Session = Depends(get_db),
        user_id: int,
        current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    获取用户的岗位
    """
    # 检查用户是否存在
    user = crud.user.get(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )

    # 获取用户岗位
    if not user.job:
        raise HTTPException(
            status_code=404,
            detail="用户未分配岗位"
        )

    return Response(data=user.job, message="获取用户岗位成功")

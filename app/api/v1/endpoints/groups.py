from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api.dependencies import get_current_active_user, get_current_active_superuser
from app.schemas.response import ResponseModel as Response, PageResponseModel, PageData
from app.db.session import get_db

router = APIRouter()


@router.get("", response_model=PageResponseModel[schemas.Group])
def read_groups(
        db: Session = Depends(get_db),
        name: Optional[str] = None,
        status: Optional[str] = None,
        current: int = 0,
        size: int = 100,
        current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    获取岗位列表
    """
    group, total = crud.group.get_multi(db, skip=current, limit=size, name=name, status=status)
    page_data = PageData(
        total=total,
        records=group
    )
    return Response(data=page_data, message="获取分组列表成功")


@router.get("/{group_id}", response_model=Response[schemas.Group])
def read_group(
        *,
        db: Session = Depends(get_db),
        group_id: int,
        current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    获取分组详情
    """
    groups = crud.group.get(db, group_id=group_id)
    if not groups:
        raise HTTPException(
            status_code=404,
            detail="分组不存在"
        )
    return Response(data=groups, message="获取分组详情成功")


@router.post("", response_model=Response[schemas.Group])
def create_group(
        *,
        db: Session = Depends(get_db),
        group_in: schemas.GroupCreate,
        current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    创建新分组
    """
    # 检查分组名称是否已存在
    if group_in.group_name:
        exists = crud.group.get_by_name(db, name=group_in.group_name)
        if exists:
            raise HTTPException(
                status_code=400,
                detail="分组名称已存在"
            )

    # 创建新分组
    group = crud.group.create(db, obj_in=group_in)
    return Response(data=group, message="创建分组成功")


@router.put("/{group_id}", response_model=Response[schemas.Group])
def update_group(
        *,
        db: Session = Depends(get_db),
        group_id: int,
        group_in: schemas.GroupUpdate,
        current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    更新分组
    """
    group = crud.group.get(db, group_id=group_id)
    if not group:
        raise HTTPException(
            status_code=404,
            detail="分组不存在"
        )

    if group_in.group_name:
        exists = crud.group.get_by_name(db, name=group_in.group_name)
        if exists and exists.group_id != group_id:
            raise HTTPException(
                status_code=400,
                detail="分组名称已存在"
            )

    group = crud.group.update(db, db_obj=group, obj_in=group_in)
    return Response(data=group, message="更新分组成功")


@router.delete("/{group_id}", response_model=Response[schemas.Group])
def delete_group(
        *,
        db: Session = Depends(get_db),
        group_id: int,
        current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    删除分组
    """
    group = crud.group.get(db, group_id=group_id)
    if not group:
        raise HTTPException(
            status_code=404,
            detail="分组不存在"
        )

    # 检查是否有关联的角色、功能、菜单或组件
    if crud.role.get_by_group(db, group_id=group_id) or \
            crud.function.get_by_group(db, group_id=group_id) or \
            crud.component.get_by_group(db, group_id=group_id):
        raise HTTPException(
            status_code=400,
            detail="分组下有关联的角色或权限，不能删除"
        )

    group = crud.group.remove(db, group_id=group_id)
    return Response(data=group, message="删除分组成功")

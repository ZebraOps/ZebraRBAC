from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.schemas.response import ResponseModel as Response, PageResponseModel, PageData
from app.api.dependencies import get_current_active_user, get_current_active_superuser
from app.db.session import get_db

router = APIRouter()


@router.get("", response_model=PageResponseModel[schemas.Component])
def read_components(
        db: Session = Depends(get_db),
        name: Optional[str] = None,
        status: Optional[str] = None,
        current: int = 0,
        size: int = 100,
        current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    获取组件列表
    """
    component, total = crud.component.get_multi(db, skip=current, limit=size, name=name, status=status)
    page_data = PageData(
        total=total,
        records=component
    )
    return Response(data=page_data, message="获取组件数据成功")


@router.post("", response_model=Response[schemas.Component])
def create_component(
        *,
        db: Session = Depends(get_db),
        component_in: schemas.ComponentCreate,
        current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    创建新组件
    """
    # 检查分组是否存在
    group = crud.group.get(db, group_id=component_in.group_id)
    if not group:
        raise HTTPException(
            status_code=404,
            detail="分组不存在"
        )

    # 检查组件名称在分组内是否唯一
    if crud.component.get_by_name_and_group(db, name=component_in.component_name, group_id=component_in.group_id):
        raise HTTPException(
            status_code=400,
            detail="组件名称在该分组内已存在"
        )

    component = crud.component.create(db, obj_in=component_in)
    return Response(data=component, message="创建组件成功")


@router.get("/{component_id}", response_model=Response[schemas.Component])
def read_component(
        *,
        db: Session = Depends(get_db),
        component_id: int,
        current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    获取组件详情
    """
    component = crud.component.get(db, component_id=component_id)
    if not component:
        raise HTTPException(
            status_code=404,
            detail="组件不存在"
        )
    return Response(data=component, message="查看组件详情成功")


@router.put("/{component_id}", response_model=Response[schemas.Component])
def update_component(
        *,
        db: Session = Depends(get_db),
        component_id: int,
        component_in: schemas.ComponentUpdate,
        current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    更新组件
    """
    component = crud.component.get(db, component_id=component_id)
    if not component:
        raise HTTPException(
            status_code=404,
            detail="组件不存在"
        )

    # 如果要更新分组，检查分组是否存在
    if component_in.group_id and component_in.group_id != component.group_id:
        group = crud.group.get(db, group_id=component_in.group_id)
        if not group:
            raise HTTPException(
                status_code=404,
                detail="分组不存在"
            )

    # 如果要更新组件名称，检查新名称在分组内是否唯一
    if component_in.component_name and component_in.component_name != component.component_name:
        group_id = component_in.group_id if component_in.group_id else component.group_id
        if crud.component.get_by_name_and_group(db, name=component_in.component_name, group_id=group_id,
                                                exclude_id=component_id):
            raise HTTPException(
                status_code=400,
                detail="组件名称在该分组内已存在"
            )

    component = crud.component.update(db, db_obj=component, obj_in=component_in)
    return Response(data=component, message="更新组件成功")


@router.delete("/{component_id}", response_model=Response[schemas.Component])
def delete_component(
        *,
        db: Session = Depends(get_db),
        component_id: int,
        current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    删除组件
    """
    component = crud.component.get(db, component_id=component_id)
    if not component:
        raise HTTPException(
            status_code=404,
            detail="组件不存在"
        )

    # 检查是否有角色关联此组件
    if crud.component.has_roles(db, component_id=component_id):
        raise HTTPException(
            status_code=400,
            detail="有角色关联此组件，不能删除"
        )

    component = crud.component.remove(db, component_id=component_id)
    return Response(data=component, message="删除组件成功")

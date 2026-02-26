from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.schemas.response import ResponseModel as Response, PageResponseModel, PageData
from app.api.dependencies import get_current_active_user, get_current_active_superuser
from app.db.session import get_db

router = APIRouter()


@router.get("", response_model=PageResponseModel[schemas.Function])
def read_functions(
        db: Session = Depends(get_db),
        name: Optional[str] = None,
        group_id: Optional[int] = None,
        status: Optional[str] = None,
        uri: Optional[str] = None,
        current: int = 0,
        size: int = 100,
        current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    获取功能点列表
    """

    functions, total = crud.function.get_multi(db,
                                               skip=current,
                                               limit=size,
                                               name=name,
                                               group_id=group_id,
                                               status=status,
                                               uri=uri)
    page_data = PageData(
        total=total,
        records=functions
    )
    return Response(data=page_data, message="功能数据获取成功")


@router.post("", response_model=Response[schemas.Function])
def create_function(
        *,
        db: Session = Depends(get_db),
        function_in: schemas.FunctionCreate,
        current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    创建新功能点
    """
    # 检查分组是否存在
    group = crud.group.get(db, group_id=function_in.group_id)
    if not group:
        raise HTTPException(
            status_code=404,
            detail="分组不存在"
        )

    # 检查功能点名称在分组内是否唯一
    if crud.function.get_by_name_and_group(db, name=function_in.func_name, group_id=function_in.group_id):
        raise HTTPException(
            status_code=400,
            detail="功能点名称在该分组内已存在"
        )

    # 检查URI和请求方法组合是否唯一
    if crud.function.get_by_uri_and_method(db, uri=function_in.uri, method_type=function_in.method_type):
        raise HTTPException(
            status_code=400,
            detail="URI和请求方法组合已存在"
        )

    function = crud.function.create(db, obj_in=function_in)
    return Response(data=function, message="接口创建成功")


@router.get("/{func_id}", response_model=Response[schemas.Function])
def read_function(
        *,
        db: Session = Depends(get_db),
        func_id: int,
        current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    获取功能点详情
    """
    function = crud.function.get(db, func_id=func_id)
    if not function:
        raise HTTPException(
            status_code=404,
            detail="功能点不存在"
        )
    return Response(data=function, message="接口查询成功")


@router.put("/{func_id}", response_model=Response[schemas.Function])
def update_function(
        *,
        db: Session = Depends(get_db),
        func_id: int,
        function_in: schemas.FunctionUpdate,
        current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    更新功能点
    """
    function = crud.function.get(db, func_id=func_id)
    if not function:
        raise HTTPException(
            status_code=404,
            detail="功能点不存在"
        )

    # 如果要更新分组，检查分组是否存在
    if function_in.group_id and function_in.group_id != function.group_id:
        group = crud.group.get(db, group_id=function_in.group_id)
        if not group:
            raise HTTPException(
                status_code=404,
                detail="分组不存在"
            )

    # 如果要更新功能点名称，检查新名称在分组内是否唯一
    if function_in.func_name and function_in.func_name != function.func_name:
        group_id = function_in.group_id if function_in.group_id else function.group_id
        if crud.function.get_by_name_and_group(db, name=function_in.func_name, group_id=group_id, exclude_id=func_id):
            raise HTTPException(
                status_code=400,
                detail="功能点名称在该分组内已存在"
            )

    # 如果要更新URI或请求方法，检查组合是否唯一
    if (function_in.uri and function_in.uri != function.uri) or \
            (function_in.method_type and function_in.method_type != function.method_type):
        uri = function_in.uri if function_in.uri else function.uri
        method_type = function_in.method_type if function_in.method_type else function.method_type
        if crud.function.get_by_uri_and_method(db, uri=uri, method_type=method_type, exclude_id=func_id):
            raise HTTPException(
                status_code=400,
                detail="URI和请求方法组合已存在"
            )

    function = crud.function.update(db, db_obj=function, obj_in=function_in)
    return Response(data=function, message="接口更新成功")


@router.delete("/{func_id}", response_model=Response[schemas.Function])
def delete_function(
        *,
        db: Session = Depends(get_db),
        func_id: int,
        current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    删除功能点
    """
    function = crud.function.get(db, func_id=func_id)
    if not function:
        raise HTTPException(
            status_code=404,
            detail="功能点不存在"
        )

    # 检查是否有角色关联此功能点
    if crud.function.has_roles(db, func_id=func_id):
        raise HTTPException(
            status_code=400,
            detail="有角色关联此功能点，不能删除"
        )

    function = crud.function.remove(db, func_id=func_id)
    return Response(data=function, message="接口删除成功")

from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.schemas.response import ResponseModel as Response, PageResponseModel, PageData
from app.api.dependencies import get_current_active_user, get_current_active_superuser
from app.db.session import get_db

router = APIRouter()


@router.get("", response_model=PageResponseModel[schemas.Role])
def read_roles(
        db: Session = Depends(get_db),
        name: Optional[str] = None,
        group_id: Optional[int] = None,
        status: Optional[str] = None,
        current: int = 0,
        size: int = 100,
        current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    获取角色列表
    """
    roles, total = crud.role.get_multi(db, skip=current, limit=size, name=name, group_id=group_id, status=status)
    page_data = PageData(
        total=total,
        records=roles
    )
    return Response(data=page_data, message="获取角色列表成功")


@router.post("", response_model=Response[schemas.Role])
def create_role(
        *,
        db: Session = Depends(get_db),
        role_in: schemas.RoleCreate,
        current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    创建新角色
    """
    # 检查分组是否存在
    group = crud.group.get(db, group_id=role_in.group_id)
    if not group:
        raise HTTPException(
            status_code=404,
            detail="分组不存在"
        )

    # 检查角色名在分组内是否唯一
    if crud.role.get_by_name_and_group(db, name=role_in.role_name, group_id=role_in.group_id):
        raise HTTPException(
            status_code=400,
            detail="角色名称在该分组内已存在"
        )

    role = crud.role.create(db, obj_in=role_in)
    return Response(data=role, message="创建角色成功")


@router.get("/{role_id}", response_model=Response[schemas.Role])
def read_role(
        *,
        db: Session = Depends(get_db),
        role_id: int,
        current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    获取角色详情
    """
    role = crud.role.get(db, role_id=role_id)
    if not role:
        raise HTTPException(
            status_code=404,
            detail="角色不存在"
        )
    return Response(data=role, message="获取角色详情成功")


@router.put("/{role_id}", response_model=Response[schemas.Role])
def update_role(
        *,
        db: Session = Depends(get_db),
        role_id: int,
        role_in: schemas.RoleUpdate,
        current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    更新角色
    """
    role = crud.role.get(db, role_id=role_id)
    if not role:
        raise HTTPException(
            status_code=404,
            detail="角色不存在"
        )

    # 如果要更新分组，检查分组是否存在
    if role_in.group_id and role_in.group_id != role.group_id:
        group = crud.group.get(db, group_id=role_in.group_id)
        if not group:
            raise HTTPException(
                status_code=404,
                detail="分组不存在"
            )

    # 如果要更新角色名，检查新名称在分组内是否唯一
    if role_in.role_name and role_in.role_name != role.role_name:
        group_id = role_in.group_id if role_in.group_id else role.group_id
        if crud.role.get_by_name_and_group(db, name=role_in.role_name, group_id=group_id, exclude_id=role_id):
            raise HTTPException(
                status_code=400,
                detail="角色名称在该分组内已存在"
            )

    role = crud.role.update(db, db_obj=role, obj_in=role_in)
    return Response(data=role, message="角色更新成功")


@router.delete("/{role_id}", response_model=Response[schemas.Role])
def delete_role(
        *,
        db: Session = Depends(get_db),
        role_id: int,
        current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    删除角色
    """
    role = crud.role.get(db, role_id=role_id)
    if not role:
        raise HTTPException(
            status_code=404,
            detail="角色不存在"
        )

    # 检查是否有用户关联此角色
    if crud.role.has_users(db, role_id=role_id):
        raise HTTPException(
            status_code=400,
            detail="有用户关联此角色，不能删除"
        )

    role = crud.role.remove(db, role_id=role_id)
    return Response(data=role, message="角色删除成功")


@router.get("/{role_id}/users", response_model=Response[List[schemas.User]])
def get_role_users(
        *,
        db: Session = Depends(get_db),
        role_id: int,
        current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    获取角色关联的用户列表
    """
    # 检查角色是否存在
    role = crud.role.get(db, role_id=role_id)
    if not role:
        raise HTTPException(
            status_code=404,
            detail="角色不存在"
        )

    # 获取角色关联的用户
    users = crud.role.get_role_users(db, role_id=role_id)

    return Response(data=users, message="获取角色用户列表成功")


@router.post("/{role_id}/users", response_model=Response[List[schemas.User]])
def assign_users_to_role(
        *,
        db: Session = Depends(get_db),
        role_id: int,
        user_ids: List[int],
        current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    为角色分配用户
    """
    # 检查角色是否存在
    role = crud.role.get(db, role_id=role_id)
    if not role:
        raise HTTPException(
            status_code=404,
            detail="角色不存在"
        )

    # 检查用户是否存在
    users = []
    for user_id in user_ids:
        user = crud.user.get(db, user_id=user_id)
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"用户ID {user_id} 不存在"
            )
        users.append(user)

    # 为角色分配用户
    assigned_users = crud.role.assign_users(db, role_id=role_id, user_ids=user_ids)

    return Response(data=assigned_users, message="用户分配成功")


@router.delete("/{role_id}/users", response_model=Response[List[schemas.User]])
def remove_role_users(
        *,
        db: Session = Depends(get_db),
        role_id: int,
        user_ids: List[int],
        current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    移除角色关联的用户
    """
    # 检查角色是否存在
    role = crud.role.get(db, role_id=role_id)
    if not role:
        raise HTTPException(
            status_code=404,
            detail="角色不存在"
        )

    # 检查用户是否存在
    for user_id in user_ids:
        user = crud.user.get(db, user_id=user_id)
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"用户ID {user_id} 不存在"
            )

    # 移除角色关联的用户
    remaining_users = crud.role.remove_users(db, role_id=role_id, user_ids=user_ids)

    return Response(data=remaining_users, message="用户移除成功")


@router.get("/{role_id}/menus", response_model=Response[List[schemas.Menu]])
def get_role_menus(
        *,
        db: Session = Depends(get_db),
        role_id: int,
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    获取角色关联的菜单列表
    """
    # 检查角色是否存在
    role = crud.role.get(db, role_id=role_id)
    if not role:
        raise HTTPException(
            status_code=404,
            detail="角色不存在"
        )

    # 获取角色关联的菜单
    menus = crud.role.get_role_menus(db, role_id=role_id, skip=skip, limit=limit)

    return Response(data=menus, message="获取角色菜单列表成功")


@router.post("/{role_id}/menus", response_model=Response[List[schemas.Menu]])
def assign_menus_to_role(
        *,
        db: Session = Depends(get_db),
        role_id: int,
        menu_ids: List[int],
        current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    为角色分配菜单
    """
    # 检查角色是否存在
    role = crud.role.get(db, role_id=role_id)
    if not role:
        raise HTTPException(
            status_code=404,
            detail="角色不存在"
        )

    # 检查菜单是否存在
    menus = []
    for menu_id in menu_ids:
        menu = crud.menu.get(db, menu_id=menu_id)
        if not menu:
            raise HTTPException(
                status_code=404,
                detail=f"菜单ID {menu_id} 不存在"
            )
        menus.append(menu)

    # 为角色分配菜单
    assigned_menus = crud.role.assign_menus(db, role_id=role_id, menu_ids=menu_ids)

    return Response(data=assigned_menus, message="菜单分配成功")


@router.delete("/{role_id}/menus", response_model=Response[List[schemas.Menu]])
def remove_role_menus(
        *,
        db: Session = Depends(get_db),
        role_id: int,
        menu_ids: List[int],
        current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    移除角色关联的菜单
    """
    # 检查角色是否存在
    role = crud.role.get(db, role_id=role_id)
    if not role:
        raise HTTPException(
            status_code=404,
            detail="角色不存在"
        )

    # 检查菜单是否存在
    for menu_id in menu_ids:
        menu = crud.menu.get(db, menu_id=menu_id)
        if not menu:
            raise HTTPException(
                status_code=404,
                detail=f"菜单ID {menu_id} 不存在"
            )

    # 移除角色关联的菜单
    remaining_menus = crud.role.remove_menus(db, role_id=role_id, menu_ids=menu_ids)

    return Response(data=remaining_menus, message="菜单移除成功")


@router.get("/{role_id}/components", response_model=Response[List[schemas.Component]])
def get_role_components(
        *,
        db: Session = Depends(get_db),
        role_id: int,
        current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    获取角色关联的组件列表
    """
    # 检查角色是否存在
    role = crud.role.get(db, role_id=role_id)
    if not role:
        raise HTTPException(
            status_code=404,
            detail="角色不存在"
        )

    # 获取角色关联的组件
    components = crud.role.get_role_components(db, role_id=role_id)

    return Response(data=components, message="获取角色组件列表成功")


@router.post("/{role_id}/components", response_model=Response[List[schemas.Component]])
def assign_components_to_role(
        *,
        db: Session = Depends(get_db),
        role_id: int,
        component_ids: List[int],
        current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    为角色分配组件
    """
    # 检查角色是否存在
    role = crud.role.get(db, role_id=role_id)
    if not role:
        raise HTTPException(
            status_code=404,
            detail="角色不存在"
        )

    # 检查组件是否存在
    components = []
    for component_id in component_ids:
        component = crud.component.get(db, component_id=component_id)
        if not component:
            raise HTTPException(
                status_code=404,
                detail=f"组件ID {component_id} 不存在"
            )
        components.append(component)

    # 为角色分配组件
    assigned_components = crud.role.assign_components(db, role_id=role_id, component_ids=component_ids)

    return Response(data=assigned_components, message="组件分配成功")


@router.delete("/{role_id}/components", response_model=Response[List[schemas.Component]])
def remove_role_components(
        *,
        db: Session = Depends(get_db),
        role_id: int,
        component_ids: List[int],
        current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    移除角色关联的组件
    """
    # 检查角色是否存在
    role = crud.role.get(db, role_id=role_id)
    if not role:
        raise HTTPException(
            status_code=404,
            detail="角色不存在"
        )

    # 检查组件是否存在
    for component_id in component_ids:
        component = crud.component.get(db, component_id=component_id)
        if not component:
            raise HTTPException(
                status_code=404,
                detail=f"组件ID {component_id} 不存在"
            )

    # 移除角色关联的组件
    remaining_components = crud.role.remove_components(db, role_id=role_id, component_ids=component_ids)

    return Response(data=remaining_components, message="组件移除成功")


"""
角色和功能
"""


@router.get("/{role_id}/functions", response_model=Response[List[schemas.Function]])
def get_role_functions(
        *,
        db: Session = Depends(get_db),
        role_id: int,
        current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    获取角色关联的功能点列表
    """
    # 检查角色是否存在
    role = crud.role.get(db, role_id=role_id)
    if not role:
        raise HTTPException(
            status_code=404,
            detail="角色不存在"
        )

    # 获取角色关联的功能点
    functions = crud.role.get_role_functions(db, role_id=role_id)

    return Response(data=functions, message="获取角色功能点列表成功")


@router.post("/{role_id}/functions", response_model=Response[List[schemas.Function]])
def assign_functions_to_role(
        *,
        db: Session = Depends(get_db),
        role_id: int,
        function_ids: List[int],
        current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    为角色分配功能点
    """
    # 检查角色是否存在
    role = crud.role.get(db, role_id=role_id)
    if not role:
        raise HTTPException(
            status_code=404,
            detail="角色不存在"
        )

    # 检查功能点是否存在
    functions = []
    for function_id in function_ids:
        function = crud.function.get(db, func_id=function_id)
        if not function:
            raise HTTPException(
                status_code=404,
                detail=f"功能点ID {function_id} 不存在"
            )
        functions.append(function)

    # 为角色分配功能点
    assigned_functions = crud.role.assign_functions(db, role_id=role_id, function_ids=function_ids)

    return Response(data=assigned_functions, message="功能点分配成功")


@router.delete("/{role_id}/functions", response_model=Response[List[schemas.Function]])
def remove_role_functions(
        *,
        db: Session = Depends(get_db),
        role_id: int,
        function_ids: List[int],
        current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    移除角色关联的功能点
    """
    # 检查角色是否存在
    role = crud.role.get(db, role_id=role_id)
    if not role:
        raise HTTPException(
            status_code=404,
            detail="角色不存在"
        )

    # 检查功能点是否存在
    for function_id in function_ids:
        function = crud.function.get(db, func_id=function_id)
        if not function:
            raise HTTPException(
                status_code=404,
                detail=f"功能点ID {function_id} 不存在"
            )

    # 移除角色关联的功能点
    remaining_functions = crud.role.remove_functions(db, role_id=role_id, function_ids=function_ids)

    return Response(data=remaining_functions, message="功能点移除成功")

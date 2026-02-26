from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.schemas.response import ResponseModel as Response, PageResponseModel, PageData
from app.api.dependencies import get_current_active_user, get_current_active_superuser
from app.db.session import get_db

router = APIRouter()


@router.get("", response_model=PageResponseModel[schemas.Menu])
def read_menus(
        db: Session = Depends(get_db),
        name: Optional[str] = None,
        status: Optional[str] = None,
        current: int = 0,
        size: int = 100,
        current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    获取菜单列表
    """
    group, total = crud.menu.get_multi(db, skip=current, limit=size, name=name, status=status)
    page_data = PageData(
        total=total,
        records=group
    )
    return Response(data=page_data, message="获取分组列表成功")


@router.get("/tree", response_model=Response[List[schemas.MenuTree]])
def read_menus_tree(
        db: Session = Depends(get_db),
        name: Optional[str] = None,
        status: Optional[str] = None,
        path: Optional[str] = None,
        current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    获取菜单树状结构
    """
    menus_tree = crud.menu.get_menu_tree(db, name=name, status=status, path=path)
    return Response(data=menus_tree, message="获取菜单树成功")


@router.post("", response_model=Response[schemas.Menu])
def create_menu(
        *,
        db: Session = Depends(get_db),
        menu_in: schemas.MenuCreate,
        current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    创建新菜单
    """
    # 检查父菜单是否存在
    if menu_in.parent_id:
        parent_menu = crud.menu.get(db, menu_id=menu_in.parent_id)
        if not parent_menu:
            raise HTTPException(
                status_code=404,
                detail="父菜单不存在"
            )
    # 检查菜单名称是否已存在
    existing_menu = crud.menu.get_by_name(db, name=menu_in.menu_name)
    if existing_menu:
        raise HTTPException(
            status_code=409,
            detail="菜单名称已存在"
        )

    menu = crud.menu.create(db, obj_in=menu_in)
    return Response(data=menu, message="菜单创建成功")


@router.get("/{menu_id}", response_model=Response[schemas.Menu])
def read_menu(
        *,
        db: Session = Depends(get_db),
        menu_id: int,
        current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    获取菜单详情
    """
    menu = crud.menu.get(db, menu_id=menu_id)
    if not menu:
        raise HTTPException(
            status_code=404,
            detail="菜单不存在"
        )
    return Response(data=menu, message="菜单详情获取成功")


@router.put("/{menu_id}", response_model=Response[schemas.Menu])
def update_menu(
        *,
        db: Session = Depends(get_db),
        menu_id: int,
        menu_in: schemas.MenuUpdate,
        current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    更新菜单
    """
    menu = crud.menu.get(db, menu_id=menu_id)
    if not menu:
        raise HTTPException(
            status_code=404,
            detail="菜单不存在"
        )

    # 如果要更新父菜单，检查父菜单是否存在
    if menu_in.parent_id and menu_in.parent_id != menu.parent_id:
        parent_menu = crud.menu.get(db, menu_id=menu_in.parent_id)
        if not parent_menu:
            raise HTTPException(
                status_code=404,
                detail="父菜单不存在"
            )

    menu = crud.menu.update(db, db_obj=menu, obj_in=menu_in)
    return Response(data=menu, message="菜单更新获取成功")


@router.delete("/{menu_id}", response_model=Response[schemas.Menu])
def delete_menu(
        *,
        db: Session = Depends(get_db),
        menu_id: int,
        current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    删除菜单
    """
    menu = crud.menu.get(db, menu_id=menu_id)
    if not menu:
        raise HTTPException(
            status_code=404,
            detail="菜单不存在"
        )

    # 检查是否有子菜单
    if crud.menu.get_by_parent(db, parent_id=menu_id):
        raise HTTPException(
            status_code=400,
            detail="存在子菜单，不能删除"
        )

    # 检查是否有角色关联此菜单
    if crud.menu.has_roles(db, menu_id=menu_id):
        raise HTTPException(
            status_code=400,
            detail="有角色关联此菜单，不能删除"
        )

    menu = crud.menu.remove(db, menu_id=menu_id)
    return Response(data=menu, message="菜单删除成功")

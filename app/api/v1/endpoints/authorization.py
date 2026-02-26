# app/api/v1/endpoints/authorization.py
from typing import Any, List, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.schemas.response import ResponseModel as Response
from app.api.dependencies import get_current_active_user
from app.db.session import get_db

router = APIRouter()

@router.get("", response_model=Response[Dict])
def get_user_authorization(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    获取当前登录用户的权限信息，包括角色、菜单、功能点等
    """
    try:
        # 获取用户角色
        user_roles = crud.user.get_user_roles(db, user_id=current_user.user_id)
        role_ids = [role.role_id for role in user_roles]

        # 判断用户是否为管理员（检查是否拥有超级管理员角色）
        is_admin = crud.user.is_superuser(current_user)

        # 获取用户菜单权限（树状结构）
        user_menus = []
        if role_ids:
            menus = crud.menu.get_menus_by_roles(db, role_ids=role_ids)
            # 构建菜单树
            user_menus = _extract_menu_paths(menus)

        # 获取用户功能点权限
        user_functions = []
        if role_ids:
            functions = crud.function.get_functions_by_roles(db, role_ids=role_ids)
            user_functions = [func.uri for func in functions if func.uri]

        # 获取用户组件权限
        # 获取用户组件权限
        user_components = {}
        if role_ids:
            components = crud.component.get_components_by_roles(db, role_ids=role_ids)
            user_components = {comp.component_name: True for comp in components}

        # 构建返回数据
        auth_data = {
            "userId": current_user.user_id,
            "userName": current_user.username,
            "email": current_user.email,
            "nickName": current_user.nickname,
            "avatar": current_user.avatar,
            "menus": {
                "all": is_admin,
                "data": user_menus if not is_admin else {}
            },
            "permissions": {
                "all": is_admin,
                "functions": user_functions,
                "components": user_components
            }
        }

        return Response(data=auth_data, message="获取用户权限信息成功")

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取权限信息失败: {str(e)}"
        )


def _extract_menu_paths(menu_items: List[models.Menu]) -> Dict[str, bool]:
    """
    从菜单列表中提取所有路径，构建成 {path: true} 的字典格式
    包含完整路径和父级路径，例如：/permission/menus 会生成 /permission/menus 和 /permission
    """
    paths = {}

    # 收集所有菜单项
    def collect_all_paths(menus):
        for menu in menus:
            # 获取菜单路径
            if hasattr(menu, 'path') and menu.path:
                full_path = menu.path
            elif isinstance(menu, dict) and 'path' in menu and menu['path']:
                full_path = menu['path']
            else:
                continue

            # 添加完整路径
            paths[full_path] = True

            # 添加所有父级路径
            path_parts = full_path.strip('/').split('/')
            if len(path_parts) > 1:
                for i in range(1, len(path_parts)):
                    parent_path = '/' + '/'.join(path_parts[:i])
                    paths[parent_path] = True

            # 递归处理子菜单
            if hasattr(menu, 'children') and menu.children:
                collect_all_paths(menu.children)
            elif isinstance(menu, dict) and 'children' in menu and menu['children']:
                collect_all_paths(menu['children'])

    collect_all_paths(menu_items)
    return paths


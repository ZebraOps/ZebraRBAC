from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.schemas.response import ResponseModel as Response
from app.api.dependencies import get_current_active_user, get_current_active_superuser
from app.db.session import get_db

router = APIRouter()


@router.get("", response_model=Response[List[schemas.Organization]])
def read_organizations(
    db: Session = Depends(get_db),
    current: int = 0,
    size: int = 100,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    获取组织列表
    """
    organizations = crud.organization.get_multi(db, skip=current, limit=size)
    return Response(data=organizations, message="获取组织列表成功")


@router.get("/tree", response_model=Response[List[schemas.OrganizationTree]])
def read_organizations_tree(
    db: Session = Depends(get_db),
    name: Optional[str] = None,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    获取组织树状结构
    """
    try:
        organizations_tree = crud.organization.get_org_tree(db, name=name)
        return Response(data=organizations_tree, message="获取组织树成功")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取组织树失败: {str(e)}"
        )


@router.post("", response_model=Response[schemas.Organization])
def create_organization(
    *,
    db: Session = Depends(get_db),
    organization_in: schemas.OrganizationCreate,
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    创建新组织
    """
    # 检查组织编码是否唯一
    if crud.organization.get_by_code(db, code=organization_in.org_code):
        raise HTTPException(
            status_code=400,
            detail="组织编码已存在"
        )

    # 检查父组织是否存在
    if organization_in.parent_id:
        parent_org = crud.organization.get(db, org_id=organization_in.parent_id)
        if not parent_org:
            raise HTTPException(
                status_code=404,
                detail="父组织不存在"
            )
    # 确保根节点的 parent_id 为 None 而不是 0
    if organization_in.parent_id == 0:
        organization_in.parent_id = None

    organization = crud.organization.create(db, obj_in=organization_in)
    return Response(data=organization, message="创建组织成功")


@router.get("/{org_id}", response_model=Response[schemas.Organization])
def read_organization(
    *,
    db: Session = Depends(get_db),
    org_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    获取组织详情
    """
    organization = crud.organization.get(db, org_id=org_id)
    if not organization:
        raise HTTPException(
            status_code=404,
            detail="组织不存在"
        )
    return Response(data=organization, message="获取组织详情成功")


@router.put("/{org_id}", response_model=Response[schemas.Organization])
def update_organization(
    *,
    db: Session = Depends(get_db),
    org_id: int,
    organization_in: schemas.OrganizationUpdate,
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    更新组织
    """
    organization = crud.organization.get(db, org_id=org_id)
    if not organization:
        raise HTTPException(
            status_code=404,
            detail="组织不存在"
        )

    # 检查组织编码是否唯一
    if organization_in.org_code and organization_in.org_code != organization.org_code:
        if crud.organization.get_by_code(db, code=organization_in.org_code):
            raise HTTPException(
                status_code=400,
                detail="组织编码已存在"
            )

    # 处理 parent_id，将 0 转换为 None
    if hasattr(organization_in, 'parent_id') and organization_in.parent_id is not None:
        if organization_in.parent_id == 0:
            # 将 0 转换为 None 表示根节点
            organization_in.parent_id = None
        elif organization_in.parent_id != organization.parent_id:
            # 检查父组织是否存在（如果不是设置为根节点）
            parent_org = crud.organization.get(db, org_id=organization_in.parent_id)
            if not parent_org:
                raise HTTPException(
                    status_code=404,
                    detail="父组织不存在"
                )

    # 防止组织成为自己的父组织
    if organization_in.parent_id == org_id:
        raise HTTPException(
            status_code=400,
            detail="组织不能成为自己的父组织"
        )

    organization = crud.organization.update(db, db_obj=organization, obj_in=organization_in)
    return Response(data=organization, message="更新组织成功")


@router.delete("/{org_id}", response_model=Response[schemas.Organization])
def delete_organization(
    *,
    db: Session = Depends(get_db),
    org_id: int,
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    删除组织
    """
    organization = crud.organization.get(db, org_id=org_id)
    if not organization:
        raise HTTPException(
            status_code=404,
            detail="组织不存在"
        )

    # 检查是否有子组织
    children = db.query(models.Organization).filter(models.Organization.parent_id == org_id).first()
    if children:
        raise HTTPException(
            status_code=400,
            detail="该组织下有子组织，不能删除"
        )

    # 检查是否有用户关联
    user_orgs = crud.user_organization.get_by_org(db, org_id=org_id)
    if user_orgs:
        raise HTTPException(
            status_code=400,
            detail="该组织下有关联用户，不能删除"
        )

    organization = crud.organization.remove(db, org_id=org_id)
    return Response(data=organization, message="删除组织成功")

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.schemas.response import ResponseModel as Response
from app.api.dependencies import get_current_active_user, get_current_active_superuser
from app.db.session import get_db

router = APIRouter()


@router.get("/user/{user_id}", response_model=Response[List[schemas.user_organization_response.UserOrganizationResponse]])
def read_user_organizations(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    获取用户组织职务关联列表
    """
    # 检查用户是否存在
    user = crud.user.get(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )

    user_organizations = crud.user_organization.get_by_user(db, user_id=user_id)
    return Response(data=user_organizations, message="获取用户组织职务关联列表成功")


@router.post("/", response_model=Response[schemas.UserOrganization])
def create_user_organization(
    *,
    db: Session = Depends(get_db),
    user_org_in: schemas.UserOrganizationCreate,
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    创建用户组织职务关联
    """
    # 检查用户是否存在
    user = crud.user.get(db, user_id=user_org_in.user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )

    # 检查组织是否存在
    organization = crud.organization.get(db, org_id=user_org_in.org_id)
    if not organization:
        raise HTTPException(
            status_code=404,
            detail="组织不存在"
        )

    # 检查职务是否存在
    position = crud.position.get(db, position_id=user_org_in.position_id)
    if not position:
        raise HTTPException(
            status_code=404,
            detail="职务不存在"
        )

    # 检查是否已存在关联
    existing = db.query(models.UserOrganization).filter(
        models.UserOrganization.user_id == user_org_in.user_id,
        models.UserOrganization.org_id == user_org_in.org_id,
        models.UserOrganization.position_id == user_org_in.position_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="用户组织职务关联已存在"
        )

    user_organization = crud.user_organization.create(db, obj_in=user_org_in)
    return Response(data=user_organization, message="创建用户组织职务关联成功")


@router.put("/{user_org_id}/primary", response_model=Response[schemas.UserOrganization])
def set_primary_user_organization(
    *,
    db: Session = Depends(get_db),
    user_org_id: int,
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    设置用户主岗
    """
    user_org = crud.user_organization.get(db, id=user_org_id)
    if not user_org:
        raise HTTPException(
            status_code=404,
            detail="用户组织职务关联不存在"
        )

    user_org = crud.user_organization.set_primary(
        db,
        user_id=user_org.user_id,
        org_id=user_org.org_id,
        position_id=user_org.position_id
    )

    return Response(data=user_org, message="设置主岗成功")


@router.delete("/{user_org_id}", response_model=Response[schemas.UserOrganization])
def delete_user_organization(
    *,
    db: Session = Depends(get_db),
    user_org_id: int,
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    删除用户组织职务关联
    """
    user_org = crud.user_organization.get(db, id=user_org_id)
    if not user_org:
        raise HTTPException(
            status_code=404,
            detail="用户组织职务关联不存在"
        )

    user_org = crud.user_organization.remove(db, id=user_org_id)
    return Response(data=user_org, message="删除用户组织职务关联成功")

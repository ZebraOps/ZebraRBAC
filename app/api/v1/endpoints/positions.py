from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.schemas.response import ResponseModel as Response, PageResponseModel, PageData
from app.api.dependencies import get_current_active_user, get_current_active_superuser
from app.db.session import get_db

router = APIRouter()


@router.get("", response_model=PageResponseModel[schemas.Position])
def read_positions(
    db: Session = Depends(get_db),
    name: Optional[str] = None,
    code: Optional[str] = None,
    current: int = 0,
    size: int = 100,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    获取职务列表
    """
    positions, total = crud.position.get_multi(db, skip=current, limit=size, position_name=name, position_code=code)
    page_data = PageData(
        total=total,
        records=positions
    )

    return Response(data=page_data, message="获取职务列表成功")


@router.post("", response_model=Response[schemas.Position])
def create_position(
    *,
    db: Session = Depends(get_db),
    position_in: schemas.PositionCreate,
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    创建新职务
    """
    position = crud.position.create(db, obj_in=position_in)
    return Response(data=position, message="创建职务成功")


@router.get("/{position_id}", response_model=Response[schemas.Position])
def read_position(
    *,
    db: Session = Depends(get_db),
    position_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    获取职务详情
    """
    position = crud.position.get(db, position_id=position_id)
    if not position:
        raise HTTPException(
            status_code=404,
            detail="职务不存在"
        )
    return Response(data=position, message="获取职务详情成功")


@router.put("/{position_id}", response_model=Response[schemas.Position])
def update_position(
    *,
    db: Session = Depends(get_db),
    position_id: int,
    position_in: schemas.PositionUpdate,
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    更新职务
    """
    position = crud.position.get(db, position_id=position_id)
    if not position:
        raise HTTPException(
            status_code=404,
            detail="职务不存在"
        )

    position = crud.position.update(db, db_obj=position, obj_in=position_in)
    return Response(data=position, message="更新职务成功")


@router.delete("/{position_id}", response_model=Response[schemas.Position])
def delete_position(
    *,
    db: Session = Depends(get_db),
    position_id: int,
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    删除职务
    """
    position = crud.position.get(db, position_id=position_id)
    if not position:
        raise HTTPException(
            status_code=404,
            detail="职务不存在"
        )

    # 检查是否有用户关联
    user_orgs = db.query(models.UserOrganization).filter(
        models.UserOrganization.position_id == position_id
    ).first()

    if user_orgs:
        raise HTTPException(
            status_code=400,
            detail="该职务下有关联用户，不能删除"
        )

    position = crud.position.remove(db, position_id=position_id)
    return Response(data=position, message="删除职务成功")

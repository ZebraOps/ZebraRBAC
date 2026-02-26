from datetime import timedelta
from typing import Any, Union

from fastapi import Request
from fastapi import APIRouter, Depends, HTTPException, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import crud, schemas
from app.schemas.response import ResponseModel as Response
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.token import CustomTokenResponse, TokenData
from app.api.dependencies import get_current_active_user
from app.core import security
from app.core.config import settings
from app.db.session import get_db

router = APIRouter()


# 添加用于表单数据的模型
class UserLoginForm(BaseModel):
    username: str
    password: str


@router.post("/swagger-token", response_model=schemas.Token)
def login_access_token(
        db: Session = Depends(get_db),
        form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    用于swagger文档的登录接口
    """
    user = crud.user.authenticate(db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="用户被禁用")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.user_id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/access-token", response_model=CustomTokenResponse)
def login_access_token(
        request: Request,
        user_data: Union[schemas.UserLogin, UserLoginForm],
        db: Session = Depends(get_db)
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    仅支持 application/json 格式
    """
    client_ip = request.client.host
    user = crud.user.authenticate(db, username=user_data.username, password=user_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="用户被禁用")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.user_id, expires_delta=access_token_expires
    )
    refresh_token = security.create_access_token(
        user.user_id, expires_delta=refresh_token_expires
    )
    user.last_ip = client_ip
    db.add(user)
    db.commit()

    return CustomTokenResponse(
        data=TokenData(
            token=access_token,
            refreshToken=refresh_token
        ),
        code=200,
        message="请求成功"
    )


@router.post("/refresh-token", response_model=CustomTokenResponse)
def refresh_token(
        refresh_data: schemas.RefreshTokenRequest,
        db: Session = Depends(get_db)
) -> Any:
    """
    Refresh access token using refresh token
    """
    # 验证刷新令牌并获取用户信息
    payload = security.verify_token(refresh_data.refreshToken)
    if not payload:
        raise HTTPException(status_code=401, detail="无效的刷新令牌")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="令牌无效")

    user = crud.user.get(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="用户被禁用")

    # 生成新的访问令牌和刷新令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    new_access_token = security.create_access_token(
        user.user_id, expires_delta=access_token_expires
    )
    new_refresh_token = security.create_access_token(
        user.user_id, expires_delta=refresh_token_expires
    )

    return CustomTokenResponse(
        data=TokenData(
            token=new_access_token,
            refreshToken=new_refresh_token
        ),
        code=200,
        message="请求成功"
    )

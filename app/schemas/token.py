from typing import Optional
from pydantic import BaseModel


class TokenData(BaseModel):
    token: str
    refreshToken: str


class Token(BaseModel):
    access_token: str
    token_type: str


class CustomTokenResponse(BaseModel):
    data: TokenData
    code: int = 200
    message: str = "请求成功"


class TokenPayload(BaseModel):
    sub: Optional[int] = None


class RefreshTokenRequest(BaseModel):
    refreshToken: str

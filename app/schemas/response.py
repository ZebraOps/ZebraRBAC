from typing import Generic, Optional, TypeVar, List
from pydantic import BaseModel
from fastapi import status

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    code: int = status.HTTP_200_OK
    message: str = "Success"
    data: Optional[T] = None


class PageData(BaseModel, Generic[T]):
    total: int
    records: List[T]


class PageResponseModel(BaseModel, Generic[T]):
    code: int = status.HTTP_200_OK
    message: str = "Success"
    data: Optional[PageData[T]] = None

from typing import Any, Generic, List, Optional, TypeVar

from ninja import Schema

D = TypeVar("D")
I = TypeVar("I")


class BaseResponse(Schema, Generic[D]):
    success: bool = True
    message: Optional[str] = None
    data: Optional[D] = None


class PaginatedDataBase(Schema, Generic[I]):
    items: List[I]
    total_items: int
    current_page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_previous: bool
    next_page_number: Optional[int] = None
    previous_page_number: Optional[int] = None


class ErrorDetail(Schema):
    code: Optional[str] = None
    message: str
    field: Optional[str] = None


class ErrorResponse(Schema):
    success: bool = False
    message: str = "An error occurred."
    errors: Optional[List[ErrorDetail]] = None
    data: Optional[Any] = None

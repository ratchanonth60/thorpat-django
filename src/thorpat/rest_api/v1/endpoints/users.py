from ninja import Router
from ninja.params.functions import Query

from thorpat.apps.users.models import User
from thorpat.rest_api.schemas.base_schemas import BaseResponse, PaginatedDataBase
from thorpat.rest_api.schemas.users import UserFilterSchema, UserSchema
from django.core.paginator import Paginator as CorePaginator

router = Router(tags=["users"])


@router.get("/", response=BaseResponse[PaginatedDataBase[UserSchema]])
def get_users_manual_pagination(
    request,
    page: int = Query(1, description="Page number, starting from 1"),
    per_page: int = Query(10, gt=0, lt=101, description="Items per page (1-100)"),
    order_by: str = Query("id", description="Order by field"),
    # --- Filter Parameters ---
    filters: UserFilterSchema = Query(None, description="Filter parameters for users"),
):
    """
    Retrieves a paginated and filtered list of users,
    with pagination handled manually and the response wrapped in BaseResponse.
    """
    queryset = filters.filter(User.objects.all())  # Apply filters from UserFilterSchema
    queryset = queryset.order_by(order_by)
    # --- Pagination ---
    # หมายเหตุ: Paginator ที่ถูกต้องควร import จาก from django.core.paginator import Paginator
    # ถ้าคุณใช้ from django.contrib.admin.options import Paginator อาจมีพฤติกรรมไม่ตรงตามที่คาดหวังสำหรับ API ทั่วไป
    django_paginator = CorePaginator(queryset, per_page)

    page_obj = django_paginator.get_page(page)

    paginated_data_for_schema = {
        "items": list(page_obj.object_list),
        "total_items": django_paginator.count,
        "current_page": page_obj.number,
        "per_page": django_paginator.per_page,
        "total_pages": django_paginator.num_pages,
        "has_next": page_obj.has_next(),
        "has_previous": page_obj.has_previous(),
        "next_page_number": page_obj.next_page_number()
        if page_obj.has_next()
        else None,
        "previous_page_number": page_obj.previous_page_number()
        if page_obj.has_previous()
        else None,
    }

    # สร้าง instance ของ PaginatedDataBase[UserSchema] ก่อนส่งให้ BaseResponse
    # เพื่อให้ Pydantic/Ninja ทำการ validate และ convert types ได้ถูกต้อง (โดยเฉพาะ list of items)
    # paginated_data_object = PaginatedDataBase[UserSchema](**paginated_data_for_schema) # ไม่จำเป็นต้องทำขั้นตอนนี้ถ้า schema ตรงกันแล้ว

    return BaseResponse(
        success=True,
        message="Successfully retrieved users",
        # data=paginated_data_object # ส่ง object ที่ validate แล้ว
        data=paginated_data_for_schema,  # ส่ง dict ตรงๆ ก็ได้ Ninja/Pydantic จะ validate เอง
    )

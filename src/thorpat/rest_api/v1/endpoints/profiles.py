from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.errors import HttpError

from thorpat.apps.profiles.models import Address
from thorpat.rest_api.schemas.base_schemas import (
    BaseResponse,
)
from thorpat.rest_api.schemas.profiles import (
    AddressCreateSchema,
    AddressSchema,
    AddressUpdateSchema,
)

# ใช้ auth=JWTAuth() เพื่อให้ endpoint ทั้งหมดใน router นี้ต้องมีการยืนยันตัวตน
# ถ้าบาง endpoint ไม่ต้องการ auth ให้ใส่ auth=None ที่ decorator ของ endpoint นั้นๆ
router = Router(tags=["profiles"])


@router.post("/addresses/", response=BaseResponse[AddressSchema])
def create_address(request: HttpRequest, payload: AddressCreateSchema):
    """
    Create a new address for the authenticated user.
    """

    # สร้าง Address object แต่ยังไม่ save ลง db เพื่อใส่ user ก่อน
    address_data = payload.dict(exclude_unset=True)

    # ตรวจสอบว่า country code ที่ส่งมาถูกต้องหรือไม่ (django-countries จะจัดการเรื่องนี้เมื่อ save)
    # แต่ถ้าต้องการ validate ก่อน save ก็ทำได้

    try:
        address = Address(user=request.user, **address_data)
        address.full_clean()  # เรียก model validation
        address.save()  # save() method ที่ override ไว้จะจัดการเรื่อง is_default
        return BaseResponse(
            success=True, message="Address created successfully.", data=address
        )
    except Exception as e:  #  จับ ValidationError จาก full_clean() หรืออื่นๆ
        # ควร log error e
        raise HttpError(400, str(e))


@router.get("/addresses/{address_id}/", response=BaseResponse[AddressSchema])
def retrieve_address(request: HttpRequest, address_id: int):
    """
    Retrieve a specific address by its ID for the authenticated user.
    """

    address = get_object_or_404(Address, id=address_id, user=request.user)

    return BaseResponse(success=True, data=address)


@router.put("/addresses/{address_id}/", response=BaseResponse[AddressSchema])
def update_address(request: HttpRequest, address_id: int, payload: AddressUpdateSchema):
    """
    Update a specific address by its ID for the authenticated user.
    """

    address = get_object_or_404(Address, id=address_id, user=request.user)

    update_data = payload.dict(
        exclude_unset=True
    )  # exclude_unset=True จะเอาเฉพาะ field ที่ส่งมา

    for attr, value in update_data.items():
        setattr(address, attr, value)

    try:
        address.full_clean()  # เรียก model validation
        address.save()  # save() method ที่ override ไว้จะจัดการเรื่อง is_default
        return BaseResponse(
            success=True, message="Address updated successfully.", data=address
        )
    except Exception as e:
        raise HttpError(400, str(e))


@router.delete("/addresses/{address_id}/", response=BaseResponse)  # 204 No Content ก็ได้
def delete_address(request: HttpRequest, address_id: int):
    """
    Delete a specific address by its ID for the authenticated user.
    """

    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.delete()
    return BaseResponse(success=True, message="Address deleted successfully.")

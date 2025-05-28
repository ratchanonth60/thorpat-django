from typing import Optional

import phonenumbers
from ninja import ModelSchema, Schema
from pydantic import ValidationInfo, field_validator

from thorpat.apps.profiles.models import Address


class AddressSchema(ModelSchema):
    # user: UserSchema # ถ้าต้องการแสดงข้อมูล user เต็มๆ
    user_id: int  # หรือจะใช้ user_id เพื่อความง่ายในการสร้าง/อัปเดต

    class Meta:
        model = Address
        fields = "__all__"  # หรือระบุ fields ที่ต้องการ
        # exclude = ['user'] # ถ้าใช้ user_id แทน


class AddressCreateSchema(Schema):
    # user_id: int # เราจะใช้ request.user แทน หรือถ้า admin สร้างให้คนอื่นก็อาจจะใส่
    address_line_1: str
    address_line_2: Optional[str] = None
    city: str
    state_province: Optional[str] = None
    postal_code: str
    country: str  # รหัสประเทศ เช่น "TH", "US"
    phone_number: Optional[str] = None
    address_type: Optional[str] = None
    is_default_shipping: Optional[bool] = False
    is_default_billing: Optional[bool] = False

    @field_validator("phone_number")
    @classmethod
    def validate_and_format_phone(
        cls, v: Optional[str], info: ValidationInfo
    ) -> Optional[str]:
        if not v:
            return None
        country_code = info.data.get("country") if info.data else None
        try:
            parsed_number = phonenumbers.parse(v, region=country_code)
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValueError("The phone number entered is not valid.")
            return phonenumbers.format_number(
                parsed_number, phonenumbers.PhoneNumberFormat.E164
            )
        except phonenumbers.NumberParseException:
            raise ValueError("Invalid phone number format.")
        except Exception as e:
            raise ValueError(f"Could not process phone number: {e}")


class AddressUpdateSchema(Schema):
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    city: Optional[str] = None
    state_province: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None  # รหัสประเทศ เช่น "TH", "US"
    phone_number: Optional[str] = None
    address_type: Optional[str] = None
    is_default_shipping: Optional[bool] = None  # ใช้ None เพื่อให้สามารถส่ง false ได้
    is_default_billing: Optional[bool] = None

    @field_validator("phone_number")
    @classmethod
    def validate_and_format_phone_update(
        cls, v: Optional[str], info: ValidationInfo
    ) -> Optional[str]:
        # For update, we might need to re-fetch country if it's not part of update payload
        # but this validator assumes it's either provided or phone is already E.164 or None
        if not v:
            return None  # Allow clearing the phone number

        # If country is also being updated, use that, otherwise it's harder without DB access here
        country_code = (
            info.data.get("country") if info.data and "country" in info.data else None
        )

        try:
            # A bit simplified for update: if country isn't changing, this works best if 'v' is E.164 or region is set in model
            parsed_number = phonenumbers.parse(v, region=country_code)
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValueError("The phone number entered is not valid.")
            return phonenumbers.format_number(
                parsed_number, phonenumbers.PhoneNumberFormat.E164
            )
        except phonenumbers.NumberParseException:
            raise ValueError("Invalid phone number format.")
        except Exception as e:
            raise ValueError(f"Could not process phone number: {e}")

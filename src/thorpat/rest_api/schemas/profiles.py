from typing import Optional

import phonenumbers
from ninja import ModelSchema, Schema
from pydantic import ValidationInfo, field_validator

from thorpat.apps.profiles.models import Address


class AddressSchema(ModelSchema):
    class Meta:
        model = Address  # Your Django Address model
        fields = [
            "id",
            "user",  # Or just user if it resolves to the ID or a nested schema
            "address_line_1",
            "address_line_2",
            "city",
            "state_province",
            "postal_code",
            "phone_number",
            "country",  # This will now correctly handle None from the model
            "address_type",
            "is_default_shipping",
            "is_default_billing",
            "created_at",
            "updated_at",
        ]
        # exclude = ['user'] # If using user_id instead of the full user object

    @staticmethod
    def resolve_phone_number(obj):
        if not obj.phone_number:
            return
        print(f"Resolving phone number for address ID {obj.id}: {obj.phone_number}")
        return f"{obj.phone_number}"

    @staticmethod
    def resolve_country(obj):
        if not obj.country:
            return
        print(f"Resolving country for address ID {obj.id}: {obj.country}")
        return f"{obj.country.code}"


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

from typing import Any, Dict, Optional

from ninja import Field, Schema
from pydantic import field_validator


class UserRegisterSchema(Schema):
    username: str
    email: str
    password: str = Field(..., min_length=8)
    password_confirm: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    @field_validator("password_confirm")
    @classmethod
    def passwords_match(cls, v: str, values: Dict[str, Any]) -> str:
        """Validates that password_confirm matches password."""
        # values.data contains the already validated fields
        # For Pydantic v2, values is a ValidationInfo object, access data with values.data
        # For Pydantic v1, values is a dict of field values

        if "password" in values.data and v != values.data["password"]:
            raise ValueError("Passwords do not match")
        return v


class EmailConfirmationSchema(Schema):
    token: str


class PasswordResetRequestSchema(Schema):
    email: str


class PasswordResetConfirmSchema(Schema):
    token: str
    new_password: str = Field(..., min_length=8)  # เพิ่ม min_length ตัวอย่าง
    new_password_confirm: str

    @field_validator("new_password_confirm")
    @classmethod
    def new_passwords_match(cls, v: str, values: Dict[str, Any]) -> str:
        if "new_password" in values.data and v != values.data["new_password"]:
            raise ValueError("New passwords do not match")
        return v


class MessageResponseSchema(Schema):
    message: str

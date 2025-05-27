from typing import Optional
from ninja import Field, ModelSchema, FilterSchema

from thorpat.apps.users.models import User


class UserSchema(ModelSchema):
    class Meta:
        model = User
        fields = "__all__"
        exclude = (
            "password",
            "last_login",
            "is_superuser",
            "groups",
            "user_permissions",
        )


class UserFilterSchema(FilterSchema):
    first_name: Optional[str] = Field(None, q="first_name__icontains")
    last_name: Optional[str] = Field(None, q="last_name__icontains")
    email: Optional[str] = Field(None, q="email__icontains")
    username: Optional[str] = Field(None, q="username__icontains")
    is_active: Optional[bool] = Field(True, q="is_active")

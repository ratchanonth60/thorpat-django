from django.contrib.auth import authenticate
from django.http import HttpRequest
from ninja import Router
from ninja.errors import HttpError

from thorpat.apps.users.models import User
from thorpat.rest_api.schemas.token import LoginSchema, TokenResponseSchema
from thorpat.rest_api.utils import generate_access_token, generate_refresh_token
from thorpat.rest_api.schemas.base_schemas import BaseResponse

router = Router(tags=["authentication"], auth=None)


@router.post(
    "/login", response=BaseResponse[TokenResponseSchema]
)  # auth=None to bypass global auth
def login(request: HttpRequest, data: LoginSchema):
    user = authenticate(username=data.username, password=data.password)
    if user is not None and isinstance(
        user, User
    ):  # Check if user is an instance of your User model
        access_token = generate_access_token(user)
        refresh_token_str = generate_refresh_token(user)  # If implementing refresh
        return BaseResponse(
            success=True,
            message="Login successful",
            data=TokenResponseSchema(
                access_token=access_token,
                refresh_token=refresh_token_str,  # If implementing refresh
            ),
        )
    raise HttpError(401, "Invalid username or password")

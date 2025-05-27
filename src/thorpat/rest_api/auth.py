from typing import Any, Optional

from django.http import HttpRequest
from ninja.errors import HttpError
from ninja.security import HttpBearer

from thorpat.apps.users.models import User

from .utils import decode_token


class JWTAuth(HttpBearer):
    def authenticate(self, request: HttpRequest, token: str) -> Optional[Any]:
        decoded_payload = decode_token(token)
        if not decoded_payload:
            return None  # Or raise an exception like HttpError(401, "Invalid token")

        # Ensure it's an access token if you differentiate
        if decoded_payload.get("token_type") != "access":
            # Optionally raise an error if it's not an access token
            # from ninja.errors import HttpError
            raise HttpError(401, "Invalid token type")

        try:
            user = User.objects.get(id=decoded_payload.get("user_id"))
            # You can attach more info from the token to the request if needed
            # request.auth_payload = decoded_payload
            return (
                user  # Return the user object for Django Ninja to populate request.auth
            )
        except User.DoesNotExist:  # type: ignore[no-untyped-except]
            raise HttpError(401, "User not found")
        except (
            Exception
        ):  # Broad exception for other potential issues during user retrieval
            return None

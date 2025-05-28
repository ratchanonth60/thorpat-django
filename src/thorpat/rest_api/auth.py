import logging
from typing import Optional

from django.http import HttpRequest
from ninja.errors import AuthenticationError, HttpError
from ninja.security import HttpBearer

from thorpat.apps.users.models import User

from .utils import decode_token

log = logging.getLogger(__name__)


class JWTAuth(HttpBearer):
    def authenticate(
        self, request: HttpRequest, token: str
    ) -> Optional[User]:  # Be more specific with return type
        decoded_payload = decode_token(token)
        if decoded_payload.get("token_type") != "access" or not decoded_payload:
            log.error("Invalid token type or empty payload")
            raise AuthenticationError(message="Invalid token")

        user_id_from_token = decoded_payload.get("user_id")
        if user_id_from_token is None:
            # Optionally, raise an error or log this, as a valid token should have a user_id
            return None

        try:
            # Ensure user_id_from_token is an int if your User model's PK is an int
            # This check might be overly cautious if your JWT creation guarantees an int,
            # but it satisfies MyPy.
            if not isinstance(user_id_from_token, int):
                # You could attempt conversion `int(user_id_from_token)`
                # or simply reject if type is not as expected.
                raise AuthenticationError(message="Invalid user ID format in token")

            user = User.objects.get(id=user_id_from_token)
            return user
        except User.DoesNotExist:
            raise HttpError(404, "User not found")
        except ValueError:  # If int conversion failed, or other value errors
            raise HttpError(400, "Invalid user ID in token")
        except Exception as e:  # Catching broader exceptions can be logged
            raise Exception(f"An error occurred during authentication: {str(e)}")

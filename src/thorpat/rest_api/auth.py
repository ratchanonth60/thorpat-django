import logging
from typing import Optional

from django.http import HttpRequest
from ninja.errors import AuthenticationError
from ninja.security import HttpBearer

from thorpat.apps.users.models import User

from .utils import decode_token

log = logging.getLogger(__name__)


class JWTAuth(HttpBearer):
    def authenticate(self, request: HttpRequest, token: str) -> Optional[User]:
        log.debug(f"JWTAuth: Received token: {token[:20]}...")  # Log ส่วนหนึ่งของ token
        decoded_payload = decode_token(
            token
        )  # decode_token ควรจะ raise AuthenticationError ถ้า token ผิด
        if not decoded_payload or decoded_payload.get("token_type", "") != "access":
            log.error("JWTAuth: Invalid token type or empty payload")
            # ปกติ decode_token ควรจะจัดการ error นี้แล้ว แต่ใส่ไว้เผื่อ
            raise AuthenticationError(message="Invalid token type")

        user_id_from_token = decoded_payload.get("user_id")
        log.debug(f"JWTAuth: User ID from token: {user_id_from_token}")
        if user_id_from_token is None:
            log.error("JWTAuth: No user_id in token payload")
            raise AuthenticationError(message="Invalid token payload (no user_id)")

        try:
            if not isinstance(user_id_from_token, int):
                log.error(f"JWTAuth: User ID '{user_id_from_token}' is not an int.")
                raise AuthenticationError(message="Invalid user ID format in token")

            user = User.objects.get(id=user_id_from_token)
            log.debug(
                f"JWTAuth: User '{user.username}' (ID: {user.id}) fetched successfully. is_active: {user.is_active}"
            )
            # Django Ninja จะตั้ง request.user = user ที่ return จากที่นี่
            # ไม่จำเป็นต้องเช็ค is_active ที่นี่ ถ้าต้องการให้ view จัดการ
            request.user = user
            return user
        except User.DoesNotExist:
            log.error(f"JWTAuth: User with ID {user_id_from_token} not found.")
            # Ninja คาดหวังให้ raise AuthenticationError หรือ HttpError หรือ return None
            # การ raise HttpError(404) ที่นี่อาจจะถูกจัดการโดย exception handler กลายเป็น 200
            # การ return None หรือ raise AuthenticationError จะตรงกว่าสำหรับ auth failure
            raise AuthenticationError(message="User not found from token")
        except ValueError:
            log.error(f"JWTAuth: Invalid user ID value in token: {user_id_from_token}")
            raise AuthenticationError(message="Invalid user ID in token")
        except Exception as e:
            log.error(
                f"JWTAuth: An unexpected error occurred during authentication: {str(e)}"
            )
            raise AuthenticationError(f"Authentication error: {str(e)}")

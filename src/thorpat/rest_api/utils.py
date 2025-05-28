import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import jwt
from django.conf import settings
from ninja.errors import AuthenticationError

from thorpat.apps.users.models import User

log = logging.getLogger(__name__)


def generate_access_token(user: User) -> str:
    payload = {
        "user_id": user.id,  # type: ignore
        "username": user.username,
        "exp": datetime.now(timezone.utc) + settings.JWT_ACCESS_TOKEN_LIFETIME,
        "iat": datetime.now(timezone.utc),
        "token_type": "access",  # Clarify token type
    }
    token = jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return token


# If you plan to implement refresh tokens, you'd add a similar function:
def generate_refresh_token(user: User) -> str:
    payload = {
        "user_id": user.id,  # type: ignore
        "exp": datetime.now(timezone.utc) + settings.JWT_REFRESH_TOKEN_LIFETIME,
        "iat": datetime.now(timezone.utc),
        "token_type": "refresh",
    }
    token = jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return token


def decode_token(token: str) -> Optional[Dict[str, Any]]:  # Return type hinted
    try:
        payload: Dict[str, Any] = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        log.warning("Token expired")
        raise AuthenticationError(message="Token expired")
    except jwt.InvalidTokenError as e:
        log.error(f"Invalid token: {str(e)}")
        raise AuthenticationError(message="Invalid token")
    except Exception as e:
        log.error(f"Token decoding error: {str(e)}")
        raise Exception(f"Token decoding error: {str(e)}")

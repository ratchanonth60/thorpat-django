import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import jwt
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from ninja.errors import AuthenticationError

from thorpat.apps.users.models import User

log = logging.getLogger(__name__)


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            str(user.pk)
            + str(timestamp)
            + str(user.is_active)  # Incorporate is_active for email confirmation
        )


account_activation_token = AccountActivationTokenGenerator()
password_reset_token_generator = PasswordResetTokenGenerator()


def send_confirmation_email(request: Any, user: User) -> None:
    """
    Sends an email confirmation link to the user using HTML and text templates.
    """
    token = account_activation_token.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    frontend_url = getattr(settings, "FRONTEND_URL", "127.0.0.1:8000")
    activation_link = f"{frontend_url}/confirm-email?uid={uid}&token={token}"

    subject = "Confirm your Email - Thorpat API"

    context = {
        "username": user.username,
        "activation_link": activation_link,
        "uid": uid,  # ส่ง uid เผื่อใช้ใน template โดยตรง
        "token": token,  # ส่ง token เผื่อใช้ใน template โดยตรง
    }

    # Render HTML content
    html_message = render_to_string("emails/confirmation_email.html", context)
    # Render text content (ควรสร้าง template .txt แยกต่างหากเพื่อ fallback)
    # text_message = render_to_string('emails/confirmation_email.txt', context)
    # หรือสร้างข้อความธรรมดาแบบเดิมถ้าไม่มี template .txt
    text_message = (
        f"Hi {user.username},\n\n"
        f"Please use the following link to confirm your registration:\n"
        f"{activation_link}\n\n"
        f"Alternatively, you can use the following token in the confirmation API: {token} and UID: {uid}\n\n"
        "If you did not register for an account, please ignore this email."
    )

    try:
        # django_send_mail(
        #     subject,
        #     text_message, # send text message by default
        #     settings.DEFAULT_FROM_EMAIL,
        #     [user.email],
        #     fail_silently=False,
        #     html_message=html_message # add html message
        # )

        # หรือใช้ EmailMultiAlternatives เพื่อควบคุมได้มากขึ้น
        msg = EmailMultiAlternatives(
            subject,
            text_message,  # เนื้อหาแบบ text
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )
        msg.attach_alternative(html_message, "text/html")  # เนื้อหาแบบ HTML
        msg.send(fail_silently=False)

        log.info(f"Confirmation email sent to {user.email}")
    except Exception as e:
        log.error(f"Error sending confirmation email to {user.email}: {e}")


def send_password_reset_email(request: Any, user: User) -> None:
    """
    Sends a password reset link to the user using HTML and text templates.
    """
    token = password_reset_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    frontend_url = getattr(settings, "FRONTEND_URL", "YOUR_FRONTEND_URL_NOT_SET")
    reset_link = f"{frontend_url}/reset-password?uid={uid}&token={token}"

    subject = "Password Reset Request - Thorpat API"
    context = {
        "username": user.username,
        "reset_link": reset_link,
        "uid": uid,
        "token": token,
    }

    html_message = render_to_string("emails/password_reset_email.html", context)
    # text_message = render_to_string('emails/password_reset_email.txt', context)
    text_message = (
        f"Hi {user.username},\n\n"
        f"Please use the following link to reset your password:\n"
        f"{reset_link}\n\n"
        f"Alternatively, you can use the following token in the password reset API: {token} and UID: {uid}\n\n"
        "If you did not request a password reset, please ignore this email."
    )

    try:
        msg = EmailMultiAlternatives(
            subject, text_message, settings.DEFAULT_FROM_EMAIL, [user.email]
        )
        msg.attach_alternative(html_message, "text/html")
        msg.send(fail_silently=False)
        log.info(f"Password reset email sent to {user.email}")
    except Exception as e:
        log.error(f"Error sending password reset email to {user.email}: {e}")


def validate_user_token(
    uidb64: str, token: str, token_generator: PasswordResetTokenGenerator
) -> Optional[User]:
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        return user
    return None


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

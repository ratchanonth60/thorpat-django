import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.response import Response

User = get_user_model()
log = logging.getLogger(__name__)


class AppTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            str(user.pk)
            + str(timestamp)
            + str(user.is_active)
            + str(user.password)  # Include password to invalidate on change
        )


token_generator = AppTokenGenerator()


class ResponseAPI(Response):
    def __init__(
        self,
        data=None,
        status=status.HTTP_200_OK,
        code=None,
        message=None,
        errors=None,
        **kwargs,
    ):
        if code is None:
            code = status
        response_data = {
            "code": code,
            "success": status < 300,
            "message": message if message else "Success" if status < 300 else "Failure",
            "data": data,
            "errors": errors,
        }
        super().__init__(response_data, status=status, **kwargs)


def send_password_reset_email(user):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = token_generator.make_token(user)
    reset_link = f"{settings.FRONTEND_URL}/reset-password-confirm/{uidb64}/{token}/"  # Adjust frontend route as needed

    context = {
        "username": user.username,
        "reset_link": reset_link,
    }
    email_html_message = render_to_string("emails/password_reset_email.html", context)
    email_plaintext_message = f"Hi {user.username},\n\nPlease click the link to reset your password: {reset_link}\n\nIf you did not request this, please ignore this email.\n\nThanks,\nThe Thorpat Team"

    msg = EmailMultiAlternatives(
        # Subject:
        "Password Reset Request for Your Thorpat Account",
        # Plaintext body:
        email_plaintext_message,
        # From:
        settings.DEFAULT_FROM_EMAIL,
        # To:
        [user.email],
    )
    msg.attach_alternative(email_html_message, "text/html")
    try:
        msg.send()
    except Exception as e:
        log.error(f"Error sending activation email to {user.email}: {e}")
        print(f"Error sending activation email to {user.email}: {e}")


def send_activation_email(user):
    """
    ส่งอีเมลยืนยันการลงทะเบียนไปยังผู้ใช้
    """
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = token_generator.make_token(user)  # ใช้ token_generator เดียวกันได้
    activation_link = f"{settings.FRONTEND_URL}/auth/activate/{uidb64}/{token}/"

    context = {
        "username": user.get_username(),  # หรือ user.username
        "activation_link": activation_link,
    }
    # Render HTML content จาก template
    email_html_message = render_to_string("emails/confirmation_email.html", context)

    # สร้างข้อความ plain text สำรอง
    email_plaintext_message = (
        f"Hi {user.get_username()},\n\n"
        f"Thank you for registering at Thorpat! To activate your account, "
        f"please click the link below:\n{activation_link}\n\n"
        "If you did not create an account, please ignore this email.\n\n"
        "Thanks,\nThe Thorpat Team"
    )

    msg = EmailMultiAlternatives(
        # Subject:
        "Activate Your Thorpat Account",
        # Plaintext body:
        email_plaintext_message,
        # From:
        settings.DEFAULT_FROM_EMAIL,
        # To:
        [user.email],
    )
    msg.attach_alternative(email_html_message, "text/html")
    try:
        msg.send()
    except Exception as e:
        log.error(f"Error sending activation email to {user.email}: {e}")
        print(f"Error sending activation email to {user.email}: {e}")
        # คุณอาจจะ raise error หรือ return False เพื่อให้ส่วนที่เรียกใช้ทราบว่าการส่งล้มเหลว

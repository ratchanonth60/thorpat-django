from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from thorpat.api.v1.utils import (
    token_generator,
)

User = get_user_model()


@shared_task(
    bind=True, max_retries=3, default_retry_delay=60
)  # bind=True ถ้าต้องการเข้าถึง self, retry 3 ครั้ง ทุก 60 วินาที
def send_activation_email_task(self, user_pk):
    try:
        user = User.objects.get(pk=user_pk)
        if user.is_active:
            print(f"User {user.username} is already active. Activation email not sent.")
            return f"User {user.username} is already active."

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)
        activation_link = f"{settings.FRONTEND_URL}/auth/activate/{uidb64}/{token}/"

        context = {
            "username": user.get_username(),
            "activation_link": activation_link,
        }
        email_html_message = render_to_string("emails/confirmation_email.html", context)
        email_plaintext_message = (
            f"Hi {user.get_username()},\n\n"
            f"Thank you for registering at Thorpat! To activate your account, "
            f"please click the link below:\n{activation_link}\n\n"
            "If you did not create an account, please ignore this email.\n\n"
            "Thanks,\nThe Thorpat Team"
        )

        msg = EmailMultiAlternatives(
            "Activate Your Thorpat Account",
            email_plaintext_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )
        msg.attach_alternative(email_html_message, "text/html")
        msg.send()
        return f"Activation email sent to {user.email}"
    except User.DoesNotExist:
        print(f"User with pk {user_pk} does not exist. Cannot send activation email.")
        # ไม่ต้อง retry ถ้า user ไม่มีอยู่จริง
        return f"User with pk {user_pk} does not exist."
    except Exception as exc:
        print(f"Error sending activation email to user_pk {user_pk}: {exc}")
        # Retry task ถ้าเกิด error อื่นๆ
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_password_reset_email_task(self, user_pk):
    try:
        user = User.objects.get(pk=user_pk)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)
        reset_link = (
            f"{settings.FRONTEND_URL}/apps/users/password/reset/{uidb64}/{token}/"
        )

        context = {
            "username": user.username,
            "reset_link": reset_link,
        }
        email_html_message = render_to_string(
            "emails/password_reset_email.html", context
        )
        email_plaintext_message = (
            f"Hi {user.username},\n\n"
            f"Please click the link to reset your password: {reset_link}\n\n"
            "If you did not request this, please ignore this email.\n\n"
            "Thanks,\nThe Thorpat Team"
        )

        msg = EmailMultiAlternatives(
            "Password Reset Request for Your Thorpat Account",
            email_plaintext_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )
        msg.attach_alternative(email_html_message, "text/html")
        msg.send()
        return f"Password reset email sent to {user.email}"
    except User.DoesNotExist:
        print(
            f"User with pk {user_pk} does not exist. Cannot send password reset email."
        )
        return f"User with pk {user_pk} does not exist."
    except Exception as exc:
        print(f"Error sending password reset email to user_pk {user_pk}: {exc}")
        raise self.retry(exc=exc)

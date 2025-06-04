from urllib.parse import urljoin

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter, requests
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.oauth2.views import render
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from rest_framework import generics, permissions, serializers, status
from rest_framework.mixins import Response
from rest_framework.views import APIView, Request
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from thorpat.api.v1.auth.serializers import (
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    UserRegistrationSerializer,
)
from thorpat.api.v1.utils import ResponseAPI, token_generator
from thorpat.apps.users.models import User
from thorpat.tasks.email import (
    send_activation_email_task,
    send_password_reset_email_task,
)


class CustomGoogleOAuth2Client(OAuth2Client):
    def __init__(
        self,
        request,
        consumer_key,
        consumer_secret,
        access_token_method,
        access_token_url,
        callback_url,
        _scope,  # This is fix for incompatibility between django-allauth==65.3.1 and dj-rest-auth==7.0.1
        scope_delimiter=" ",
        headers=None,
        basic_auth=False,
    ):
        super().__init__(
            request,
            consumer_key,
            consumer_secret,
            access_token_method,
            access_token_url,
            callback_url,
            scope_delimiter,
            headers,
            basic_auth,
        )


class EmptySerializer(serializers.Serializer):
    pass


class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]

    def post(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return ResponseAPI(
            serializer.validated_data,
            message="Login successfully",
            status=status.HTTP_200_OK,
        )


class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]

    def post(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return ResponseAPI(
            serializer.validated_data,
            message="Refresh token successfully",
            status=status.HTTP_200_OK,
        )


class CustomTokenVerifyView(TokenVerifyView):
    permission_classes = [permissions.AllowAny]

    def post(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return ResponseAPI(
            serializer.validated_data,
            message="Verify token successfully",
            status=status.HTTP_200_OK,
        )


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # ถ้าต้องการให้ user inactive ก่อน ให้แก้ใน serializer.create()
            # user = serializer.save(is_active=False)
            user = (
                serializer.save()
            )  # สมมติว่า is_active ถูกจัดการใน serializer หรือ model default

            if not user.is_active:  # หรือเงื่อนไขตามที่คุณต้องการสำหรับ activation
                # เรียก Celery task เพื่อส่ง activation email
                send_activation_email_task.delay(user.pk)
                message = "User registered successfully. Please check your email to activate your account."
            else:
                message = "User registered successfully."

            return ResponseAPI(
                data={"username": user.username, "email": user.email},
                message=message,
                status=status.HTTP_201_CREATED,
            )
        return ResponseAPI(
            errors=serializer.errors,
            message="Registration failed.",
            status=status.HTTP_400_BAD_REQUEST,
        )


class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            try:
                user = User.objects.get(email__iexact=email)
                # เรียก Celery task เพื่อส่ง password reset email
                send_password_reset_email_task.delay(user.pk)
            except User.DoesNotExist:
                pass  # ไม่เปิดเผยว่า user ไม่มีอยู่จริง
            return ResponseAPI(
                message="If an account with this email exists, a password reset link has been sent.",
                status=status.HTTP_200_OK,
            )
        return ResponseAPI(
            errors=serializer.errors,
            message="Invalid data.",
            status=status.HTTP_400_BAD_REQUEST,
        )


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return ResponseAPI(
                message="Password has been reset successfully. You can now login with your new password.",
                status=status.HTTP_200_OK,
            )
        return ResponseAPI(
            errors=serializer.errors,
            message="Password reset failed.",
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserAccountActivationView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = EmptySerializer

    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (
            TypeError,
            ValueError,
            OverflowError,
            User.DoesNotExist,
            UnicodeDecodeError,
        ):
            user = None

        if (
            user is not None
            and not user.is_active
            and token_generator.check_token(user, token)
        ):
            user.is_active = True
            user.save()
            return ResponseAPI(
                message="Account activated successfully. You can now login.",
                status=status.HTTP_200_OK,
            )
        elif user is not None and user.is_active:
            return ResponseAPI(
                message="Account is already active.", status=status.HTTP_200_OK
            )
        else:
            return ResponseAPI(
                message="Activation link is invalid or has expired.",
                status=status.HTTP_400_BAD_REQUEST,
            )

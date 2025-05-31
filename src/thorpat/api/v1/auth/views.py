from rest_framework import status
from rest_framework.mixins import Response
from rest_framework.views import Request
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from thorpat.api.v1.utils import ResponseAPI


class CustomTokenObtainPairView(TokenObtainPairView):
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

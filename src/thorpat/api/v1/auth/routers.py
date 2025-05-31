from django.urls import path

from thorpat.api.v1.auth.views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    CustomTokenVerifyView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    UserAccountActivationView,
    UserRegistrationView,
)

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="user_register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("verify/", CustomTokenVerifyView.as_view(), name="token_verify"),
    path(
        "activate/<str:uidb64>/<str:token>/",
        UserAccountActivationView.as_view(),
        name="account_activate",
    ),
    path(
        "password-reset/",
        PasswordResetRequestView.as_view(),
        name="password_reset_request",
    ),
    path(
        "password-reset-confirm/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
]

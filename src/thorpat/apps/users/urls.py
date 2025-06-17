from django.urls import path

from .views import (
    CustomPasswordResetCompleteView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetDoneView,
    CustomPasswordResetView,
    MobileMenuView,
    ValidateUsernameView,
    ValidateLoginFieldView,  # เพิ่ม View นี้
    ValidateEmailView,  # เพิ่ม View นี้
    ValidatePasswordView,  # เพิ่ม View นี้
    ValidatePassword2View,  # เพิ่ม View นี้
)


app_name = "users"
urlpatterns = [
    path(
        "validate-login/", ValidateLoginFieldView.as_view(), name="validate_login_field"
    ),
    path(
        "validate-username/", ValidateUsernameView.as_view(), name="validate_username"
    ),
    path("validate-email/", ValidateEmailView.as_view(), name="validate_email"),
    path(
        "validate-password/", ValidatePasswordView.as_view(), name="validate_password"
    ),
    path(
        "validate-password2/",
        ValidatePassword2View.as_view(),
        name="validate_password2",
    ),
    path("mobile-menu/", MobileMenuView.as_view(), name="mobile_menu"),
    path(
        "password/reset/",
        CustomPasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "password/reset/done/",
        CustomPasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "password/reset/<uidb64>/<token>/",
        CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password/reset/complete/",
        CustomPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]

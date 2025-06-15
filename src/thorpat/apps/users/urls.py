from django.urls import path

from .views import (
    CustomPasswordResetCompleteView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetDoneView,
    CustomPasswordResetView,
    MobileMenuView,
    ValidateUsernameView,
)

app_name = "users"
urlpatterns = [
    path(
        "validate-username/", ValidateUsernameView.as_view(), name="validate_username"
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

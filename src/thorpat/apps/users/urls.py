from django.urls import path

from .views import MobileMenuView, ValidateUsernameView

app_name = "users"
urlpatterns = [
    path(
        "validate-username/", ValidateUsernameView.as_view(), name="validate_username"
    ),
    path("mobile-menu/", MobileMenuView.as_view(), name="mobile_menu"),
]

from django.urls import path

from .users.views import UserInfoView, UserProfileUpdateView, UserRecentActivityView

app_name = "dashboard"

urlpatterns = [
    path("user/", UserInfoView.as_view(), name="user_info"),
    path("user/update/", UserProfileUpdateView.as_view(), name="user_update"),
    path(
        "user/recent-activity/",
        UserRecentActivityView.as_view(),
        name="user_recent_activity",
    ),  # <--- เพิ่ม URL นี้
]

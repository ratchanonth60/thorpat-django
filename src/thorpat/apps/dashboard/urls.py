from django.urls import path

from .users.views import UserInfoView, UserProfileUpdateView, UserRecentActivityView
from .management_views import (
    AdminOrderListView,
    AdminProductListView,
    AdminCustomerListView,
    AdminReportView,
)

app_name = "dashboard"

urlpatterns = [
    path("user/", UserInfoView.as_view(), name="user_info"),
    path("user/update/", UserProfileUpdateView.as_view(), name="user_update"),
    path(
        "user/recent-activity/",
        UserRecentActivityView.as_view(),
        name="user_recent_activity",
    ),
    path("orders/", AdminOrderListView.as_view(), name="admin_orders_list"),
    path("products/", AdminProductListView.as_view(), name="admin_products_list"),
    path("customers/", AdminCustomerListView.as_view(), name="admin_customers_list"),
    path("reports/", AdminReportView.as_view(), name="admin_reports_main"),
]

from django.urls import include, path

from .users.views import UserInfoView, UserProfileUpdateView, UserRecentActivityView

app_name = "dashboard"

urlpatterns = [
    path("user/", UserInfoView.as_view(), name="user_info"),
    path("user/update/", UserProfileUpdateView.as_view(), name="user_update"),
    path(
        "user/recent-activity/",
        UserRecentActivityView.as_view(),
        name="user_recent_activity",
    ),
    # --- Store Management Sections ---
    path(
        "products/",
        include("thorpat.apps.dashboard.product.urls", namespace="products"),
    ),
    path(
        "product-types/",
        include("thorpat.apps.dashboard.product_type.urls", namespace="product_types"),
    ),
    path(
        "partners/",
        include("thorpat.apps.dashboard.partner.urls", namespace="partners"),
    ),
    path(
        "categories/",
        include("thorpat.apps.dashboard.category.urls", namespace="categories"),
    ),
    path("orders/", include("thorpat.apps.dashboard.order.urls", namespace="orders")),
    path(
        "customers/",
        include("thorpat.apps.dashboard.customer.urls", namespace="customers"),
    ),
    path(
        "reports/", include("thorpat.apps.dashboard.report.urls", namespace="reports")
    ),
]

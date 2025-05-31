from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from thorpat.api.v1.auth.views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    CustomTokenVerifyView,
)
from thorpat.api.v1.users.routers import router as v1_users_router

urlpatterns = [
    path("v1/", include(v1_users_router.urls)),
    path(
        "v1/auth/login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path("v1/auth/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("v1/auth/verify/", CustomTokenVerifyView.as_view(), name="token_verify"),
    path("v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Optional UI:
    path(
        "v1/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "v1/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

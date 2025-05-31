from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from thorpat.api.v1.auth.routers import urlpatterns as v1_auth_urlpatterns
from thorpat.api.v1.profiles.routers import router as v1_profiles_router
from thorpat.api.v1.users.routers import router as v1_users_router

urlpatterns = [
    path("v1/", include(v1_users_router.urls)),
    path("v1/auth/", include(v1_auth_urlpatterns)),
    path("v1/profiles/", include(v1_profiles_router.urls)),
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

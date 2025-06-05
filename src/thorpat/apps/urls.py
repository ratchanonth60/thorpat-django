from django.urls import include, path


urlpatterns = [
    path("users/", include("thorpat.apps.users.urls")),
]

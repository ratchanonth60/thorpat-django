from django.urls import path

from .views import (
    AdminProductCreateView,
    AdminProductDeleteView,
    AdminProductListView,
    AdminProductUpdateView,
)

app_name = "products"

urlpatterns = [
    path("", AdminProductListView.as_view(), name="list"),
    path("add/", AdminProductCreateView.as_view(), name="add"),
    path("<int:pk>/edit/", AdminProductUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", AdminProductDeleteView.as_view(), name="delete"),
]

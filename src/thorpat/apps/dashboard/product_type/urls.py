from django.urls import path

from .views import (
    AdminProductTypeCreateView,
    AdminProductTypeDeleteView,
    AdminProductTypeListView,
    AdminProductTypeUpdateView,
)

app_name = "product_types"

urlpatterns = [
    path("", AdminProductTypeListView.as_view(), name="list"),
    path("add/", AdminProductTypeCreateView.as_view(), name="add"),
    path("<int:pk>/edit/", AdminProductTypeUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", AdminProductTypeDeleteView.as_view(), name="delete"),
]

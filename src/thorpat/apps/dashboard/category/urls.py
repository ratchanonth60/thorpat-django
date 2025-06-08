# dashboard/category/urls.py
from django.urls import path

from .views import (
    AdminCategoryCreateView,
    AdminCategoryDeleteView,
    AdminCategoryListView,
    AdminCategoryUpdateView,
)

app_name = "categories"

urlpatterns = [
    path("", AdminCategoryListView.as_view(), name="list"),
    path("add/", AdminCategoryCreateView.as_view(), name="add"),
    path("<int:pk>/edit/", AdminCategoryUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", AdminCategoryDeleteView.as_view(), name="delete"),
]

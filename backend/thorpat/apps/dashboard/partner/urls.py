from django.urls import path

from .views import (
    AdminPartnerCreateView,
    AdminPartnerDeleteView,
    AdminPartnerListView,
    AdminPartnerUpdateView,
)

app_name = "partners"

urlpatterns = [
    path("", AdminPartnerListView.as_view(), name="list"),
    path("add/", AdminPartnerCreateView.as_view(), name="add"),
    path("<int:pk>/edit/", AdminPartnerUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", AdminPartnerDeleteView.as_view(), name="delete"),
]

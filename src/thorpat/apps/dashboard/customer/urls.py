from django.urls import path

from .views import AdminCustomerListView

app_name = "customers"

urlpatterns = [
    path("", AdminCustomerListView.as_view(), name="list"),
]

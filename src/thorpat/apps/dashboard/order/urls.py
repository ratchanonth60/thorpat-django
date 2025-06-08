from django.urls import path
from .views import AdminOrderListView

app_name = "orders"

urlpatterns = [
    path("", AdminOrderListView.as_view(), name="list"),
]

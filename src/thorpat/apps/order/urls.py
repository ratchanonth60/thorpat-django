from django.urls import path

from . import views

app_name = "order"

urlpatterns = [
    # Example: /orders/
    path("", views.OrderHistoryView.as_view(), name="order_history"),
    # Example: /orders/some-uuid-number/
    path("<str:order_number>/", views.OrderDetailView.as_view(), name="order_detail"),
]

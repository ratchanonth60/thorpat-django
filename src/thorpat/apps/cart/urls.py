from django.urls import path

from . import views

app_name = "cart"

urlpatterns = [
    path("", views.CartDetailView.as_view(), name="cart_detail"),
    path("add/<int:product_id>/", views.AddToCartView.as_view(), name="add_to_cart"),
    path(
        "update/<int:line_id>/", views.UpdateCartLineView.as_view(), name="update_line"
    ),
    path(
        "remove/<int:line_id>/", views.RemoveFromCartView.as_view(), name="remove_line"
    ),
]

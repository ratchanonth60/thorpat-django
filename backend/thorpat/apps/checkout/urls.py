from django.urls import path
from . import views

app_name = "checkout"

urlpatterns = [
    path(
        "shipping/",
        views.CheckoutShippingAddressView.as_view(),
        name="shipping_address",
    ),
    path("payment/", views.CheckoutPaymentMethodView.as_view(), name="payment_method"),
    path(
        "thank-you/<str:order_number>/",
        views.OrderConfirmationView.as_view(),
        name="thank_you",
    ),
    # HTMX Endpoints for Shipping Address
    path(
        "htmx/select-address/",
        views.SelectShippingAddressHTMXView.as_view(),
        name="select_shipping_address_htmx",
    ),
    path(
        "htmx/add-address/",
        views.AddShippingAddressHTMXView.as_view(),
        name="add_shipping_address_htmx",
    ),
]

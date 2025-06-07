from django.urls import path

from . import views

app_name = "checkout"

urlpatterns = [
    path(
        "shipping-address/",
        views.CheckoutShippingAddressView.as_view(),
        name="shipping_address",
    ),
    path("payment/", views.CheckoutPaymentMethodView.as_view(), name="payment_method"),
    path(
        "thank-you/<str:order_number>/",
        views.OrderConfirmationView.as_view(),
        name="thank_you",
    ),
]

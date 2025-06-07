from django.urls import include, path


urlpatterns = [
    path("users/", include("thorpat.apps.users.urls")),
    path("cart/", include("thorpat.apps.cart.urls")),
    path("checkout/", include("thorpat.apps.checkout.urls")),
    path("products/", include("thorpat.apps.catalogue.urls")),
    path("orders/", include("thorpat.apps.order.urls")),
]

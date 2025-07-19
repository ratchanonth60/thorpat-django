from django.urls import include, path

from .users.urls import urlpatterns as users_urlpatterns
from .activitylog.urls import urlpatterns as activitylog_urlpatterns
from .cart.urls import urlpatterns as cart_urlpatterns
from .catalogue.urls import urlpatterns as catalogue_urlpatterns
from .order.urls import urlpatterns as order_urlpatterns
from .partner.urls import urlpatterns as partner_urlpatterns
from .profiles.urls import urlpatterns as profiles_urlpatterns
from .reviews.urls import urlpatterns as reviews_urlpatterns

# Import existing auth router
from thorpat.api.v1.auth.routers import urlpatterns as v1_auth_urlpatterns

urlpatterns = [
    path('users/', include(users_urlpatterns)),
    path('activitylogs/', include(activitylog_urlpatterns)),
    path('carts/', include(cart_urlpatterns)),
    path('catalogue/', include(catalogue_urlpatterns)),
    path('orders/', include(order_urlpatterns)),
    path('partners/', include(partner_urlpatterns)),
    path('profiles/', include(profiles_urlpatterns)),
    path('reviews/', include(reviews_urlpatterns)),
    path('auth/', include(v1_auth_urlpatterns)),
]
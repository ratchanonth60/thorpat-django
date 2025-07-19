from rest_framework.routers import DefaultRouter
from .views import CartViewSet, CartLineViewSet

router = DefaultRouter()
router.register(r'carts', CartViewSet)
router.register(r'cartlines', CartLineViewSet)

urlpatterns = router.urls

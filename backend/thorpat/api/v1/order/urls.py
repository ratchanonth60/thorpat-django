from rest_framework.routers import DefaultRouter
from .views import ShippingAddressViewSet, BillingAddressViewSet, OrderViewSet, OrderLineViewSet

router = DefaultRouter()
router.register(r'shippingaddresses', ShippingAddressViewSet)
router.register(r'billingaddresses', BillingAddressViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'orderlines', OrderLineViewSet)

urlpatterns = router.urls

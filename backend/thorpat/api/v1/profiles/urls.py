from rest_framework.routers import DefaultRouter
from .views import AddressViewSet

router = DefaultRouter()
router.register(r'', AddressViewSet)

urlpatterns = router.urls

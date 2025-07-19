from rest_framework.routers import DefaultRouter
from .views import ProductReviewViewSet

router = DefaultRouter()
router.register(r'', ProductReviewViewSet)

urlpatterns = router.urls

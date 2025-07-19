from rest_framework.routers import DefaultRouter
from .views import (
    ProductCategoryViewSet,
    ProductTypeViewSet,
    ProductViewSet,
    ProductAttributeViewSet,
    ProductAttributeValueViewSet,
    StockRecordViewSet,
)

router = DefaultRouter()
router.register(r'productcategories', ProductCategoryViewSet)
router.register(r'producttypes', ProductTypeViewSet)
router.register(r'products', ProductViewSet)
router.register(r'productattributes', ProductAttributeViewSet)
router.register(r'productattributevalues', ProductAttributeValueViewSet)
router.register(r'stockrecords', StockRecordViewSet)

urlpatterns = router.urls

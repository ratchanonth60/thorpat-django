from rest_framework import viewsets
from thorpat.apps.catalogue.models import (
    ProductCategory,
    ProductType,
    Product,
    ProductAttribute,
    ProductAttributeValue,
    StockRecord,
)
from .serializers import (
    ProductCategorySerializer,
    ProductTypeSerializer,
    ProductSerializer,
    ProductAttributeSerializer,
    ProductAttributeValueSerializer,
    StockRecordSerializer,
)

class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer

class ProductTypeViewSet(viewsets.ModelViewSet):
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductAttributeViewSet(viewsets.ModelViewSet):
    queryset = ProductAttribute.objects.all()
    serializer_class = ProductAttributeSerializer

class ProductAttributeValueViewSet(viewsets.ModelViewSet):
    queryset = ProductAttributeValue.objects.all()
    serializer_class = ProductAttributeValueSerializer

class StockRecordViewSet(viewsets.ModelViewSet):
    queryset = StockRecord.objects.all()
    serializer_class = StockRecordSerializer

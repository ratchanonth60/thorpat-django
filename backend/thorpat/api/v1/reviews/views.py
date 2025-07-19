from rest_framework import viewsets
from thorpat.apps.reviews.models import ProductReview
from .serializers import ProductReviewSerializer

class ProductReviewViewSet(viewsets.ModelViewSet):
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer

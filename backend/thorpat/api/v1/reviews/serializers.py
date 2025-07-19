from rest_framework import serializers
from thorpat.apps.reviews.models import ProductReview

class ProductReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = (
            "id",
            "product",
            "user",
            "rating",
            "title",
            "body",
            "is_approved",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

from rest_framework import serializers
from thorpat.apps.catalogue.models import (
    ProductCategory,
    ProductType,
    Product,
    ProductAttribute,
    ProductAttributeValue,
    StockRecord,
)

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = (
            "id",
            "user",
            "name",
            "slug",
            "description",
            "image",
        )
        read_only_fields = ("id", "slug")

class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = (
            "id",
            "name",
            "slug",
            "tracks_stock",
            "requires_shipping",
        )
        read_only_fields = ("id", "slug")

class ProductAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttribute
        fields = (
            "id",
            "product_type",
            "name",
            "code",
        )
        read_only_fields = ("id",)

class ProductAttributeValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttributeValue
        fields = (
            "id",
            "product",
            "attribute",
            "value_text",
        )
        read_only_fields = ("id",)

class StockRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockRecord
        fields = (
            "id",
            "product",
            "partner",
            "sku",
            "price_currency",
            "price_excl_tax",
            "price_incl_tax",
            "cost_price",
            "num_in_stock",
            "num_allocated",
            "low_stock_threshold",
            "date_created",
            "date_updated",
        )
        read_only_fields = ("id", "date_created", "date_updated")

class ProductSerializer(serializers.ModelSerializer):
    categories = ProductCategorySerializer(many=True, read_only=True)
    attribute_values = ProductAttributeValueSerializer(many=True, read_only=True)
    stockrecords = StockRecordSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "user",
            "product_type",
            "title",
            "slug",
            "description",
            "categories",
            "upc",
            "manufacturer",
            "dimensions",
            "weight_grams",
            "is_public",
            "created_at",
            "updated_at",
            "primary_image",
            "attribute_values",
            "stockrecords",
        )
        read_only_fields = ("id", "slug", "created_at", "updated_at")

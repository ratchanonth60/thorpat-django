from rest_framework import serializers
from thorpat.apps.cart.models import Cart, CartLine

class CartLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartLine
        fields = (
            "id",
            "cart",
            "product",
            "quantity",
            "price_excl_tax",
            "date_created",
        )
        read_only_fields = ("id", "date_created")

class CartSerializer(serializers.ModelSerializer):
    lines = CartLineSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = (
            "id",
            "owner",
            "status",
            "date_created",
            "date_merged",
            "date_submitted",
            "lines",
        )
        read_only_fields = (
            "id",
            "date_created",
            "date_merged",
            "date_submitted",
        )

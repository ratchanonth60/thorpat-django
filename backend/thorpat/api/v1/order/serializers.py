from rest_framework import serializers
from thorpat.apps.order.models import ShippingAddress, BillingAddress, Order, OrderLine

class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = "__all__"

class BillingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingAddress
        fields = "__all__"

class OrderLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderLine
        fields = "__all__"

class OrderSerializer(serializers.ModelSerializer):
    lines = OrderLineSerializer(many=True, read_only=True)
    shipping_address = ShippingAddressSerializer(read_only=True)
    billing_address = BillingAddressSerializer(read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "number",
            "cart",
            "user",
            "guest_email",
            "shipping_address",
            "billing_address",
            "total_excl_tax",
            "status",
            "date_placed",
            "lines",
        )
        read_only_fields = ("id", "number", "date_placed")

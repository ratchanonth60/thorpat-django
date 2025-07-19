from rest_framework import serializers
from thorpat.apps.profiles.models import Address

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = (
            "id",
            "user",
            "address_line_1",
            "address_line_2",
            "city",
            "state_province",
            "postal_code",
            "country",
            "phone_number",
            "address_type",
            "is_default_shipping",
            "is_default_billing",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

from django_countries.serializer_fields import CountryField
from phonenumber_field.serializerfields import (
    PhoneNumberField,
)
from rest_framework import serializers

from thorpat.apps.profiles.models import Address


class AddressSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    # หรือถ้าต้องการให้ user ปัจจุบันถูก set อัตโนมัติ:
    # user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    country = CountryField(
        country_dict=True, read_only=False
    )  # ให้ client ส่งรหัสประเทศมาได้
    phone_number = PhoneNumberField(required=False, allow_null=True)  # ทำให้ไม่บังคับ

    class Meta:
        model = Address
        fields = [
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
        ]
        read_only_fields = ("created_at", "updated_at")

    def create(self, validated_data):
        if not self.context["request"].user.is_authenticated:
            raise serializers.ValidationError(
                "User must be authenticated to create an address."
            )
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

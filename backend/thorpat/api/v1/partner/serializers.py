from rest_framework import serializers
from thorpat.apps.partner.models import Partner

class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = (
            "id",
            "user",
            "name",
            "slug",
        )
        read_only_fields = ("id", "slug")

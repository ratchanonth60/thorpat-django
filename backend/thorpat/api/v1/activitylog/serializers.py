from rest_framework import serializers
from thorpat.apps.activitylog.models import ActivityLog

class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = (
            "id",
            "user",
            "action",
            "timestamp",
            "details",
        )
        read_only_fields = ("id", "timestamp")

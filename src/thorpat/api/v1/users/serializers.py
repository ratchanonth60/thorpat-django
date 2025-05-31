from rest_framework import serializers

from thorpat.apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ("password",)

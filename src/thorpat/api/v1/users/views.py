from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated

from thorpat.api.v1.users.serializers import UserSerializer
from thorpat.apps.users.filters import UserFilter
from thorpat.apps.users.models import User


class UserView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = UserFilter
    ordering_fields = ["username", "email", "date_joined", "first_name", "last_name"]
    ordering = ["id"]

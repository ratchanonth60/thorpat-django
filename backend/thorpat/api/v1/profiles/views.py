from rest_framework import viewsets
from thorpat.apps.profiles.models import Address
from .serializers import AddressSerializer

class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

from rest_framework import viewsets
from thorpat.apps.cart.models import Cart, CartLine
from .serializers import CartSerializer, CartLineSerializer

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

class CartLineViewSet(viewsets.ModelViewSet):
    queryset = CartLine.objects.all()
    serializer_class = CartLineSerializer

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets
from rest_framework.filters import OrderingFilter

from thorpat.apps.profiles.filters import AddressFilter
from thorpat.apps.profiles.models import Address

from .serializers import AddressSerializer


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit or view it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        # if request.method in permissions.SAFE_METHODS:
        #     return True
        # Write permissions are only allowed to the owner of the address.
        return obj.user == request.user


class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsOwner,
    ]  # ผู้ใช้ต้อง login และเป็นเจ้าของ address
    filterset_class = AddressFilter

    filter_backends = [
        OrderingFilter,
        DjangoFilterBackend,
    ]  # เพิ่ม OrderingFilter
    ordering_fields = [
        "city",
        "postal_code",
        "country",
        "address_type",
        "created_at",
        "updated_at",
    ]
    ordering = ["-created_at", "id"]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            # ไม่จำเป็นต้อง order_by ที่นี่แล้วถ้าใช้ OrderingFilter และกำหนด default ordering
            return Address.objects.filter(user=user)
        return Address.objects.none()

    # perform_create ถูกย้ายไปใน serializer.create() แล้ว
    # def perform_create(self, serializer):
    #     serializer.save(user=self.request.user)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == "create":
            # สำหรับ action 'create', user ใดๆ ที่ authenticated สามารถสร้าง address ของตนเองได้
            # ไม่จำเป็นต้องมี object permission (IsOwner) เพราะยังไม่มี object
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

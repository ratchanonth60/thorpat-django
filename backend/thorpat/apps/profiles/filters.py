import django_filters
from django_countries import countries

from thorpat.apps.profiles.models import Address


class AddressFilter(django_filters.FilterSet):
    city = django_filters.CharFilter(lookup_expr="icontains")
    postal_code = django_filters.CharFilter(lookup_expr="exact")
    country = django_filters.ChoiceFilter(choices=countries)  # ให้ filter ตามรหัสประเทศ
    address_type = django_filters.CharFilter(lookup_expr="icontains")
    is_default_shipping = django_filters.BooleanFilter()
    is_default_billing = django_filters.BooleanFilter()

    class Meta:
        model = Address
        fields = [
            "city",
            "postal_code",
            "country",
            "address_type",
            "is_default_shipping",
            "is_default_billing",
        ]

import django_filters
from django import forms

from .models import Product


class ProductFilter(django_filters.FilterSet):
    # lookup_expr='icontains' คือการค้นหาแบบ case-insensitive และหาจากส่วนใดส่วนหนึ่งของคำ
    title = django_filters.CharFilter(
        lookup_expr="icontains",
        label="Search by Product Name",
        widget=forms.TextInput(
            attrs={
                "class": "w-full border-gray-300 rounded-md shadow-sm pl-10",
                "placeholder": "Search name...",
            }
        ),
    )

    # สร้าง field สำหรับกรองสถานะ is_public (Active/Inactive)
    # ใช้ ChoiceFilter เพื่อสร้าง dropdown ที่มีตัวเลือก "All", "Yes", "No"
    is_public = django_filters.ChoiceFilter(
        label="Status",
        choices=(
            ("", "All Statuses"),  # ค่าว่างสำหรับแสดงทั้งหมด
            (True, "Active / Public"),
            (False, "Inactive / Not Public"),
        ),
        widget=forms.Select(attrs={"class": "border-gray-300 rounded-md shadow-sm"}),
    )

    class Meta:
        model = Product
        fields = ["title", "is_public"]

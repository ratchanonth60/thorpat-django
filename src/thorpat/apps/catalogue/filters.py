import django_filters
from django import forms
from django.db.models import Q

from .models import Product, ProductCategory


class ProductFilter(django_filters.FilterSet):
    """
    Filter for the Product model.
    Allows searching by text and filtering by category.
    """

    search = django_filters.CharFilter(
        method="filter_search",
        label="",
        widget=forms.TextInput(
            attrs={
                "class": "form-input w-full",
                "placeholder": "Search by name...",
            }
        ),
    )

    # --- MODIFICATION START ---
    # แก้ไข 'field_name' จาก 'product_type' ที่ผิด ให้เป็น 'categories' ที่ถูกต้อง
    # เพื่อให้ตัวกรองใช้ ProductCategory ที่เลือกมา ไปกรองข้อมูลในฟิลด์ ManyToMany ที่ชื่อ 'categories' ของ Product model
    category = django_filters.ModelChoiceFilter(
        field_name="categories",
        queryset=ProductCategory.objects.all(),
        label="Category",
        empty_label="All Categories",
        widget=forms.Select(attrs={"class": "form-select w-full"}),
    )
    # --- MODIFICATION END ---

    class Meta:
        model = Product
        fields = ["search", "category"]

    def filter_search(self, queryset, name, value):
        """
        Custom filter method for the 'search' field.
        It searches for the given value in both the 'title' and 'description' fields.
        """
        if not value:
            return queryset
        return queryset.filter(
            Q(title__icontains=value) | Q(description__icontains=value)
        )

from django.contrib import admin
from phonenumber_field.serializerfields import PhoneNumberField
from phonenumber_field.widgets import (
    PhoneNumberPrefixWidget,
)

from .models import Address


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "address_line_1",
        "city",
        "country",  # แสดงประเทศ
        "phone_number",  # แสดงเบอร์โทรศัพท์
        "address_type",
        "is_default_shipping",
        "is_default_billing",
    )
    list_filter = (
        "user",
        "city",
        "country",
        "is_default_shipping",
        "is_default_billing",
        "address_type",
    )
    search_fields = (
        "user__username",
        "address_line_1",
        "city",
        "country",  # ค้นหาตามรหัสประเทศ
        "phone_number",
    )
    raw_id_fields = ("user",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("user", "address_type")}),
        (
            "Address Details",
            {
                "fields": (
                    "address_line_1",
                    "address_line_2",
                    "city",
                    "state_province",
                    "postal_code",
                    "country",  # CountryField จะแสดงเป็น dropdown
                    "phone_number",  # PhoneNumberField จะมี widget ของมันเอง
                )
            },
        ),
        ("Default Status", {"fields": ("is_default_shipping", "is_default_billing")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
    # Optional: ถ้าต้องการ widget ที่แยกรหัสประเทศกับเบอร์ใน admin
    formfield_overrides = {
        PhoneNumberField: {"widget": PhoneNumberPrefixWidget},
    }

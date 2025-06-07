from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _

from .models import BillingAddress, Order, OrderLine, ShippingAddress


class OrderLineInline(admin.TabularInline):
    model = OrderLine
    fields = (
        "product",
        "product_title",
        "quantity",
        "price_excl_tax",
        "line_price_excl_tax",
    )
    readonly_fields = fields
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "number",
        "user",
        "guest_email",
        "status",
        "total_excl_tax",
        "date_placed",
    )
    list_filter = ("status", "date_placed")
    search_fields = ("number", "user__username", "guest_email")
    readonly_fields = ("number", "user", "cart", "total_excl_tax", "date_placed")
    inlines = [OrderLineInline]
    list_editable = ("status",)
    actions = ["mark_as_shipped"]

    fieldsets = (
        (
            "Order Information",
            {"fields": ("number", "status", "user", "guest_email", "cart")},
        ),
        ("Address Information", {"fields": ("shipping_address", "billing_address")}),
        ("Financials", {"fields": ("total_excl_tax",)}),
        ("History", {"fields": ("date_placed",)}),
    )

    def has_add_permission(self, request):
        return False

    @admin.action(description=_("Mark selected orders as Shipped"))
    def mark_as_shipped(self, request, queryset):
        updated_count = queryset.update(status="Shipped")
        self.message_user(
            request,
            _("%(count)d orders were successfully marked as Shipped.")
            % {"count": updated_count},
            messages.SUCCESS,
        )


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "address_line_1", "city", "country_code")
    search_fields = ("first_name", "last_name", "address_line_1")


@admin.register(BillingAddress)
class BillingAddressAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "address_line_1", "city", "country_code")
    search_fields = ("first_name", "last_name", "address_line_1")

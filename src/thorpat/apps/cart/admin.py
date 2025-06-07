from django.contrib import admin

from .models import Cart, CartLine


class CartLineInline(admin.TabularInline):
    model = CartLine
    fields = ("product", "quantity", "price_excl_tax")
    readonly_fields = ("price_excl_tax", "date_created")
    extra = 0
    autocomplete_fields = ["product"]


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "owner",
        "status",
        "num_lines",
        "num_items",
        "total_excl_tax",
        "date_created",
    )
    list_filter = ("status", "date_created")
    search_fields = ("owner__username", "owner__email", "id")
    readonly_fields = ("date_created", "date_merged", "date_submitted", "owner")
    inlines = [CartLineInline]
    fieldsets = (
        (None, {"fields": ("owner", "status")}),
        ("Totals", {"fields": ("total_excl_tax", "num_items")}),
        ("History", {"fields": ("date_created", "date_merged", "date_submitted")}),
    )


@admin.register(CartLine)
class CartLineAdmin(admin.ModelAdmin):
    list_display = (
        "cart",
        "product",
        "quantity",
        "line_price_excl_tax",
        "date_created",
    )
    list_filter = ("cart__status", "date_created")
    search_fields = ("product__title", "cart__id")
    autocomplete_fields = ["cart", "product"]

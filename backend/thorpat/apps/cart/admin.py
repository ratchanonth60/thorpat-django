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
    # list_display can correctly show properties
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

    # --- MODIFICATION START ---
    # Add the properties to readonly_fields to display them in the detail view.
    readonly_fields = (
        "date_created",
        "date_merged",
        "date_submitted",
        "owner",
        "num_lines",
        "num_items",
        "total_excl_tax",
    )
    # --- MODIFICATION END ---

    inlines = [CartLineInline]

    # --- MODIFICATION START ---
    # Remove the properties from fieldsets.
    fieldsets = (
        (None, {"fields": ("owner", "status")}),
        # The "Totals" section is now handled by readonly_fields above.
        ("History", {"fields": ("date_created", "date_merged", "date_submitted")}),
    )
    # --- MODIFICATION END ---


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

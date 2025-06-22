from django.contrib import admin


from .models import (
    Product,
    ProductAttribute,
    ProductAttributeValue,
    ProductCategory,
    ProductType,
    StockRecord,
)


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class ProductAttributeValueInline(admin.TabularInline):  # or admin.StackedInline
    model = ProductAttributeValue
    extra = 1  # Number of empty forms to display


class StockRecordInline(admin.TabularInline):  # or admin.StackedInline
    model = StockRecord
    extra = 1
    fields = (
        "partner",
        "sku",
        "price_currency",
        "price_excl_tax",
        "num_in_stock",
    )  # Customize fields


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "slug",
        "product_type",
        "display_price",
        "is_public",
        "created_at",
    )  # Added display_price
    list_filter = ("product_type", "is_public", "categories", "created_at")
    search_fields = ("title", "description", "slug")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("categories",)
    inlines = [ProductAttributeValueInline, StockRecordInline]  # Add StockRecordInline
    fieldsets = (
        (
            None,
            {"fields": ("title", "slug", "description", "product_type", "is_public")},
        ),
        ("Categorization", {"fields": ("categories",)}),
        ("Media", {"fields": ("primary_image",)}),
        # Stock and pricing are now managed via StockRecordInline
    )
    readonly_fields = ("created_at", "updated_at")


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "product_type")
    list_filter = ("product_type",)
    search_fields = ("name", "code")


@admin.register(StockRecord)
class StockRecordAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "partner",
        "sku",
        "price_excl_tax",
        "num_in_stock",
        "date_updated",
    )
    list_filter = ("partner", "product__product_type", "date_updated")
    search_fields = ("product__title", "partner__name", "partner_sku")
    autocomplete_fields = ["product", "partner"]


# ProductAttributeValue is usually managed inline with Product,
# but you can register it separately if direct management is needed.
# @admin.register(ProductAttributeValue)
# class ProductAttributeValueAdmin(admin.ModelAdmin):
#     list_display = ('product', 'attribute', 'value_text') # Adjust based on value fields you use
#     list_filter = ('attribute', 'product__product_type')
#     search_fields = ('product__title', 'attribute__name', 'value_text')

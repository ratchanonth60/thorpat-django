from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class ProductCategory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="categories"
    )
    name = models.CharField(_("Category Name"), max_length=255, db_index=True)
    slug = models.SlugField(_("Slug"), max_length=255, unique=True, allow_unicode=True)
    description = models.TextField(_("Description"), blank=True, null=True)
    image = models.ImageField(
        _("Image"), upload_to="categories/", blank=True, null=True
    )
    # For MPTT (nested categories), you might add 'parent' ForeignKey to self
    # For now, let's keep it simple

    class Meta:
        verbose_name = _("Product Category")
        verbose_name_plural = _("Product Categories")
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            "catalogue:product_list_by_category", kwargs={"category_slug": self.slug}
        )


class ProductType(models.Model):
    """
    Defines a type of product, e.g., "Book", "T-Shirt", "Laptop".
    It can have associated attributes.
    """

    name = models.CharField(_("Product Type Name"), max_length=128, unique=True)
    slug = models.SlugField(
        _("Slug"), max_length=128, unique=True, allow_unicode=True
    )  # Optional

    tracks_stock = models.BooleanField(
        _("Track stock levels?"), default=True
    )  # Oscar has this
    requires_shipping = models.BooleanField(
        _("Requires shipping?"), default=True
    )  # Oscar has this

    class Meta:
        verbose_name = _("Product Type")
        verbose_name_plural = _("Product Types")
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class Product(models.Model):
    """
    The base product model.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="products"
    )
    product_type = models.ForeignKey(
        ProductType,
        on_delete=models.PROTECT,  # Or RESTRICT, ensure type is not deleted if products exist
        related_name="products",
        verbose_name=_("Product Type"),
        null=True,
        blank=True,  # Allow products without a specific type initially
    )
    title = models.CharField(_("Title"), max_length=255, db_index=True)
    slug = models.SlugField(_("Slug"), max_length=255, unique=True, allow_unicode=True)
    description = models.TextField(_("Description"), blank=True)
    categories = models.ManyToManyField(
        ProductCategory,
        related_name="products",
        verbose_name=_("Categories"),
        blank=True,
    )
    # UPC (Universal Product Code) / EAN / ISBN - could be an attribute or a direct field
    upc = models.CharField(
        _("UPC"), max_length=64, blank=True, null=True, unique=True, db_index=True
    )

    # Product structure: stand-alone, parent, child (for variations)
    # Oscar uses a 'structure' field and a 'parent' ForeignKey to self for this
    # For simplicity, we'll start with stand-alone products.

    is_public = models.BooleanField(
        _("Is Publicly Visible?"), default=True, db_index=True
    )
    created_at = models.DateTimeField(_("Date Created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date Updated"), auto_now=True)

    # Placeholder for images, pricing, stock - these are often in related models or more complex fields
    # For now, a simple primary image
    primary_image = models.ImageField(
        _("Primary Image"), upload_to="products/%Y/%m/", blank=True, null=True
    )

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        ordering = ["-created_at", "title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
            # Ensure slug uniqueness if generated
            original_slug = self.slug
            queryset = Product.objects.all().exclude(pk=self.pk)
            counter = 1
            while queryset.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalogue:product_detail", kwargs={"slug": self.slug})

    @property
    def primary_stockrecord(self):
        """
        Returns the first stockrecord. A more sophisticated approach might determine
        the "primary" one based on strategy (e.g., cheapest, most stock).
        """
        return self.stockrecords.first()  # type: ignore

    @property
    def display_price(self):
        """
        Returns the price from the primary stockrecord.
        Returns None if no stockrecord or price is available.
        """
        stockrecord = self.primary_stockrecord
        if stockrecord:
            return stockrecord.price_excl_tax
        return None  # Or some default/indicator that price is not available

    @property
    def is_available_to_buy(self):
        """
        Checks if the product has stock.
        """
        stockrecord = self.primary_stockrecord
        if stockrecord:
            return stockrecord.net_stock_level > 0

        return False


class ProductAttribute(models.Model):
    """
    Defines an attribute of a product type. E.g. "Color", "Size", "Author".
    """

    product_type = models.ForeignKey(
        ProductType,
        on_delete=models.CASCADE,
        related_name="attributes",
        verbose_name=_("Product Type"),
        null=True,
        blank=True,  # Can be global attribute if null
    )
    name = models.CharField(_("Attribute Name"), max_length=128)
    code = models.SlugField(
        _("Code"),
        max_length=128,
        help_text=_("Internal code for this attribute, used for lookups"),
    )  # e.g. 'color', 'book_author'

    # Attribute types: text, integer, boolean, float, option, multi_option, date, datetime, file, image
    # For simplicity, we'll start with a generic type or imply it by usage.
    # Oscar has an 'type' field.

    class Meta:
        verbose_name = _("Product Attribute")
        verbose_name_plural = _("Product Attributes")
        ordering = ["code"]
        unique_together = (
            "product_type",
            "code",
        )  # Ensure code is unique per product type

    def __str__(self):
        return self.name


class ProductAttributeValue(models.Model):
    """
    The actual value of an attribute for a specific product.
    E.g. Product: "Red T-Shirt", Attribute: "Color", Value: "Red"
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="attribute_values",
        verbose_name=_("Product"),
    )
    attribute = models.ForeignKey(
        ProductAttribute,
        on_delete=models.CASCADE,
        related_name="values",
        verbose_name=_("Attribute"),
    )
    # The value itself. Oscar uses separate fields for different types.
    # For simplicity, we can start with a CharField and handle type conversion in forms/serializers.
    # A more robust approach involves a JSONField or separate value_XXX fields.
    value_text = models.CharField(
        _("Text Value"), max_length=255, blank=True, null=True
    )
    # value_integer = models.IntegerField(_("Integer Value"), blank=True, null=True)
    # value_boolean = models.BooleanField(_("Boolean Value"), blank=True, null=True)
    # value_float = models.FloatField(_("Float Value"), blank=True, null=True)
    # value_option = models.ForeignKey('AttributeOption', ...) # If using option type

    class Meta:
        verbose_name = _("Product Attribute Value")
        verbose_name_plural = _("Product Attribute Values")
        unique_together = (
            "product",
            "attribute",
        )  # Each product can have one value for a given attribute

    def __str__(self):
        return f"{self.product.title} - {self.attribute.name}: {self.value_text or 'N/A'}"  # Simplified


class StockRecord(models.Model):
    """
    Represents the stock and pricing information for a product from a specific partner.
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="stockrecords",
        verbose_name=_("Product"),
    )
    partner = models.ForeignKey(
        "partner.Partner",
        on_delete=models.CASCADE,
        related_name="stockrecords",
        verbose_name=_("Partner"),
    )
    partner_sku = models.CharField(
        _("Partner SKU"),
        max_length=128,
        blank=True,
        db_index=True,
        help_text=_("Stock Keeping Unit, code used by the partner for this product"),
    )

    # Pricing information (simplified from Oscar's Price model)
    # Oscar has a separate Price model and currency support.
    # For simplicity, we assume a single currency for now.
    price_currency = models.CharField(
        _("Currency"), max_length=12, default="THB"
    )  # Example: 'THB', 'USD'
    price_excl_tax = models.DecimalField(
        _("Price (excluding tax)"),
        decimal_places=2,
        max_digits=12,
        validators=[
            MinValueValidator(Decimal("0.00"))
        ],  # Add MinValueValidator(Decimal('0.00')) if needed
    )
    price_incl_tax = models.DecimalField(
        _("Price (including tax)"),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )  # Oscar uses this to calculate tax")) # If you want to store this too
    cost_price = models.DecimalField(
        _("Cost Price"), max_digits=12, decimal_places=2
    )  # Price partner sells to you

    # Stock information
    num_in_stock = models.PositiveIntegerField(_("Number in Stock"), default=0)
    num_allocated = models.PositiveIntegerField(
        _("Number Allocated"), default=0, null=True, blank=True
    )  # Oscar tracks allocated stock
    low_stock_threshold = models.PositiveIntegerField(
        _("Low Stock Threshold"), blank=True, null=True
    )

    date_created = models.DateTimeField(_("Date Created"), auto_now_add=True)
    date_updated = models.DateTimeField(_("Date Updated"), auto_now=True, db_index=True)

    class Meta:
        verbose_name = _("Stock Record")
        verbose_name_plural = _("Stock Records")
        unique_together = (
            "product",
            "partner",
        )  # Each partner can only have one stock record for a product
        ordering = ["-date_created"]

    def __str__(self):
        return f"{self.product.title} from {self.partner.name} - Price: {self.price_excl_tax} {self.price_currency}, Stock: {self.num_in_stock}"

    @property
    def net_stock_level(self):
        # In Oscar, this would be num_in_stock - num_allocated (if allocated is used)
        return self.num_in_stock

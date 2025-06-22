from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from thorpat.apps.catalogue.models import Product


class Cart(models.Model):
    """
    A cart for a user, whether authenticated or anonymous.
    """

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="carts",
        verbose_name=_("Owner"),
    )

    OPEN, MERGED, SAVED, FROZEN, SUBMITTED = (
        "Open",
        "Merged",
        "Saved",
        "Frozen",
        "Submitted",
    )
    STATUS_CHOICES = (
        (OPEN, _("Open - currently active")),
        (MERGED, _("Merged - superceded by another cart")),
        (SAVED, _("Saved - for items to be bought later")),
        (FROZEN, _("Frozen - the cart cannot be modified")),
        (SUBMITTED, _("Submitted - has been ordered at the checkout")),
    )
    status = models.CharField(
        _("Status"), max_length=128, default=OPEN, choices=STATUS_CHOICES
    )

    date_created = models.DateTimeField(_("Date created"), auto_now_add=True)
    date_merged = models.DateTimeField(_("Date merged"), null=True, blank=True)
    date_submitted = models.DateTimeField(_("Date submitted"), null=True, blank=True)

    class Meta:
        verbose_name = _("Cart")
        verbose_name_plural = _("Carts")
        ordering = ["-date_created"]
        db_table = "cart"  # RENAMED from 'basket'

    def __str__(self):
        return _(
            "Cart (owner: %(owner)s, lines: %(num_lines)d, status: %(status)s)"
        ) % {
            "owner": self.owner or _("Anonymous"),
            "num_lines": self.num_lines,
            "status": self.status,
        }

    @property
    def num_lines(self):
        return self.lines.count()

    @property
    def num_items(self):
        return sum(line.quantity for line in self.lines.all())

    @property
    def total_excl_tax(self):
        total = Decimal("0.00")
        for line in self.lines.all():
            total += line.line_price_excl_tax
        return total

    @property
    def is_empty(self):
        return self.id is None or self.num_lines == 0

    def add_product(self, product, quantity=1):
        if self.status != self.OPEN:
            return

        line, created = self.lines.get_or_create(
            product=product, defaults={"quantity": quantity}
        )
        if not created:
            line.quantity += quantity
            line.save()
        return line, created


class CartLine(models.Model):  # RENAMED from Line
    """
    A line in a cart.
    """

    cart = models.ForeignKey(  # RENAMED from basket
        Cart,  # RENAMED from Basket
        on_delete=models.CASCADE,
        related_name="lines",
        verbose_name=_("Cart"),  # RENAMED from Basket
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="cart_lines",  # RENAMED from basket_lines
        verbose_name=_("Product"),
    )
    quantity = models.PositiveIntegerField(_("Quantity"), default=1)

    price_excl_tax = models.DecimalField(
        _("Price (excl. tax)"), decimal_places=2, max_digits=12, null=True, blank=True
    )

    date_created = models.DateTimeField(_("Date created"), auto_now_add=True)

    class Meta:
        verbose_name = _("Cart Line")  # RENAMED from Basket Line
        verbose_name_plural = _("Cart Lines")  # RENAMED from Basket Lines
        ordering = ["date_created"]
        unique_together = ("cart", "product")  # RENAMED from ('basket', 'product')
        db_table = "cart_line"

    def __str__(self):
        return _("Cart #%(cart_id)d, Product: %(product)s, Quantity: %(quantity)d") % {
            "cart_id": self.cart.id,
            "product": self.product.title,
            "quantity": self.quantity,
        }

    def save(self, *args, **kwargs):
        if not self.price_excl_tax and self.product.display_price:
            self.price_excl_tax = self.product.display_price
        super().save(*args, **kwargs)

    @property
    def line_price_excl_tax(self):
        if self.price_excl_tax is not None:
            return self.quantity * self.price_excl_tax
        return Decimal("0.00")

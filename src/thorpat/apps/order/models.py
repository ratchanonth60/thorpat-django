import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from thorpat.apps.catalogue.models import Product

from .abstract import AbstractAddress


class ShippingAddress(AbstractAddress):
    class Meta:
        verbose_name = _("Shipping Address")
        verbose_name_plural = _("Shipping Addresses")


class BillingAddress(AbstractAddress):
    class Meta:
        verbose_name = _("Billing Address")
        verbose_name_plural = _("Billing Addresses")


class Order(models.Model):
    number = models.CharField(
        _("Order Number"),
        max_length=128,
        db_index=True,
        unique=True,
        default=uuid.uuid4,
    )
    cart = models.ForeignKey(
        "cart.Cart", on_delete=models.SET_NULL, null=True, blank=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="orders",
        null=True,
        blank=True,
    )
    guest_email = models.EmailField(_("Guest Email"), blank=True, null=True)
    shipping_address = models.ForeignKey(
        ShippingAddress, on_delete=models.SET_NULL, null=True, blank=True
    )
    billing_address = models.ForeignKey(
        BillingAddress, on_delete=models.SET_NULL, null=True, blank=True
    )
    total_excl_tax = models.DecimalField(
        _("Order total (excl. tax)"), decimal_places=2, max_digits=12
    )
    status = models.CharField(_("Status"), max_length=100, blank=True, null=True)
    date_placed = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")
        ordering = ["-date_placed"]

    def __str__(self):
        return f"Order #{self.number}"


class OrderLine(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="lines")
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, blank=True
    )
    product_title = models.CharField(_("Product Title"), max_length=255)
    partner_sku = models.CharField(_("Partner SKU"), max_length=128, blank=True)
    quantity = models.PositiveIntegerField(_("Quantity"), default=1)
    price_excl_tax = models.DecimalField(
        _("Price per unit (excl. tax)"), decimal_places=2, max_digits=12
    )
    line_price_excl_tax = models.DecimalField(
        _("Line price (excl. tax)"), decimal_places=2, max_digits=12
    )

    class Meta:
        verbose_name = _("Order Line")
        verbose_name_plural = _("Order Lines")
        ordering = ["pk"]

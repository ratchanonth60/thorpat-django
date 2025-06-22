from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class ProductReview(models.Model):
    """
    A model for a product review.
    """

    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    product = models.ForeignKey(
        "catalogue.Product",
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name=_("Product"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name=_("User"),
    )
    rating = models.PositiveSmallIntegerField(
        _("Rating"),
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text=_("Rate the product from 1 to 5 stars."),
    )
    title = models.CharField(_("Title"), max_length=255)
    body = models.TextField(_("Body"))

    is_approved = models.BooleanField(
        _("Is Approved?"),
        default=True,
        help_text=_("Check this box to make the review public."),
    )
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)

    class Meta:
        verbose_name = _("Product Review")
        verbose_name_plural = _("Product Reviews")
        ordering = ["-created_at"]
        # Ensure a user can only review a product once
        unique_together = ("product", "user")
        db_table = "product_review"

    def __str__(self):
        return f"Review for {self.product.title} by {self.user.get_full_name()}"

from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class Partner(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="partners"
    )
    name = models.CharField(_("Partner Name"), max_length=255, unique=True)
    slug = models.SlugField(
        _("Slug"),
        max_length=255,
        unique=True,
        allow_unicode=True,
        help_text=_("Used for URLs"),
    )

    class Meta:
        # บอก Django ให้ใช้ชื่อตารางเดิมใน DB คือ 'catalogue_partner'
        db_table = "catalogue_partner"
        verbose_name = _("Partner")
        verbose_name_plural = _("Partners")
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

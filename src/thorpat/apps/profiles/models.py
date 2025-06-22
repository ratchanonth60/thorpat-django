from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField


class Address(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="addresses",
        verbose_name=_("User"),
    )
    address_line_1 = models.CharField(_("Address Line 1"), max_length=255)
    address_line_2 = models.CharField(
        _("Address Line 2"), max_length=255, blank=True, null=True
    )
    city = models.CharField(_("City"), max_length=100)
    state_province = models.CharField(
        _("State/Province"), max_length=100, blank=True, null=True
    )  # ทำให้ blank=True ได้ ถ้าบางประเทศไม่มี
    postal_code = models.CharField(_("Postal Code"), max_length=20)

    # แก้ไข field 'country'
    country = CountryField(
        _("Country"), blank_label=_("(select country)")
    )  # ใช้ CountryField

    # เพิ่ม field 'phone_number' (เป็นทางเลือก)
    phone_number = PhoneNumberField(
        _("Phone Number"), blank=True, null=True
    )  # ใช้ PhoneNumberField
    # คุณสามารถกำหนด region ได้ เช่น PhoneNumberField(region="TH") เพื่อช่วยในการ parse เบอร์ที่ไม่มีรหัสประเทศ

    address_type = models.CharField(
        _("Address Type"),
        max_length=50,
        blank=True,
        null=True,
        help_text=_("e.g., Home, Work, Billing, Shipping"),
    )
    is_default_shipping = models.BooleanField(
        _("Default Shipping Address"), default=False
    )
    is_default_billing = models.BooleanField(
        _("Default Billing Address"), default=False
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Address")
        ordering = ["-created_at"]
        db_table = "user_address"

    def __str__(self):
        return f"{self.user.username}'s address - {self.address_line_1}, {self.city}, {self.country.name}"  # แสดงชื่อประเทศ

    def save(self, *args, **kwargs):
        if self.is_default_shipping:
            Address.objects.filter(user=self.user, is_default_shipping=True).exclude(
                pk=self.pk
            ).update(is_default_shipping=False)

        if self.is_default_billing:
            Address.objects.filter(user=self.user, is_default_billing=True).exclude(
                pk=self.pk
            ).update(is_default_billing=False)

        super().save(*args, **kwargs)

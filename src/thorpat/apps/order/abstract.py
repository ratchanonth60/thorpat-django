from django.db import models
from django.utils.translation import gettext_lazy as _

from thorpat.apps.profiles.models import Address as ProfileAddress


class AbstractAddress(models.Model):
    first_name = models.CharField(_("First Name"), max_length=150, blank=True)
    last_name = models.CharField(_("Last Name"), max_length=150, blank=True)
    address_line_1 = models.CharField(_("Address Line 1"), max_length=255)
    address_line_2 = models.CharField(
        _("Address Line 2"), max_length=255, blank=True, null=True
    )
    city = models.CharField(_("City"), max_length=100)
    state_province = models.CharField(
        _("State/Province"), max_length=100, blank=True, null=True
    )
    postal_code = models.CharField(_("Postal Code"), max_length=20)
    country_code = models.CharField(_("Country Code"), max_length=2, default="TH")
    phone_number = models.CharField(_("Phone Number"), max_length=32, blank=True)

    class Meta:
        abstract = True

    def populate_from_profile_address(self, address: ProfileAddress):
        self.first_name = address.user.first_name
        self.last_name = address.user.last_name
        self.address_line_1 = address.address_line_1
        self.address_line_2 = address.address_line_2
        self.city = address.city
        self.state_province = address.state_province
        self.postal_code = address.postal_code
        self.country_code = address.country.code
        self.phone_number = str(address.phone_number) if address.phone_number else ""

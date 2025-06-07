from django import forms
from django.utils.translation import gettext_lazy as _

from thorpat.apps.profiles.models import Address


class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = Address
        # Exclude fields that are set automatically or not needed for shipping form
        exclude = ("user", "address_type", "is_default_shipping", "is_default_billing")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Tailwind CSS classes to the fields
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = (
                "appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            )

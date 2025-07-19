from django import forms
from django.utils.translation import gettext_lazy as _


class CartLineUpdateForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        label=_("Quantity"),
        widget=forms.NumberInput(
            attrs={
                "class": "w-16 text-center border-gray-300 rounded-md shadow-sm",
                "min": "1",
            }
        ),
    )


class AddToCartForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(
            attrs={
                "class": "w-20 text-center border-gray-300 rounded-md shadow-sm",
                "min": "1",
            }
        ),
    )

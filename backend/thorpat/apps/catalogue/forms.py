from django import forms

from .models import Product, ProductCategory, ProductType, StockRecord
from thorpat.apps.partner.models import Partner
from django.forms import inlineformset_factory


class ProductTypeForm(forms.ModelForm):
    class Meta:
        model = ProductType
        fields = ["name", "tracks_stock", "requires_shipping"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "block w-full mt-1 border-gray-300 rounded-md shadow-sm"
                }
            ),
            "tracks_stock": forms.CheckboxInput(
                attrs={"class": "h-4 w-4 text-indigo-600 border-gray-300 rounded"}
            ),
            "requires_shipping": forms.CheckboxInput(
                attrs={"class": "h-4 w-4 text-indigo-600 border-gray-300 rounded"}
            ),
        }


class ProductCategoryForm(forms.ModelForm):
    class Meta:
        model = ProductCategory
        fields = ["name", "description", "image"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "block w-full mt-1 border-gray-300 rounded-md shadow-sm"
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "block w-full mt-1 border-gray-300 rounded-md shadow-sm",
                    "rows": 4,
                }
            ),
            "image": forms.ClearableFileInput(
                attrs={
                    "class": "block w-full mt-1 text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
                }
            ),
        }


class ProductForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=ProductCategory.objects.none(),
        widget=forms.SelectMultiple(attrs={"class": "select select-bordered w-full"}),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        # --- ส่วนที่เพิ่มเข้ามา ---
        # รับ user ที่ถูกส่งมาจาก View
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # ถ้ามี user ถูกส่งเข้ามา (ซึ่งควรจะมีเสมอ)
        if user:
            # ให้ทำการกรอง queryset ของฟิลด์ categories
            # ให้แสดงเฉพาะ Category ที่มีเจ้าของเป็น user คนนี้เท่านั้น
            self.fields["categories"].queryset = ProductCategory.objects.filter(
                user=user
            )
        # --- จบส่วนที่เพิ่มเข้ามา ---

    class Meta:
        model = Product
        fields = [
            "product_type",
            "title",
            "description",
            "categories",
            "upc",
            "primary_image",
            "is_public",
        ]
        widgets = {
            "product_type": forms.Select(
                attrs={
                    "class": "block w-full mt-1 border-gray-300 rounded-md shadow-sm"
                }
            ),
            "title": forms.TextInput(
                attrs={
                    "class": "block w-full mt-1 border-gray-300 rounded-md shadow-sm"
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "block w-full mt-1 border-gray-300 rounded-md shadow-sm",
                    "rows": 4,
                }
            ),
            "upc": forms.TextInput(
                attrs={
                    "class": "block w-full mt-1 border-gray-300 rounded-md shadow-sm"
                }
            ),
            "primary_image": forms.ClearableFileInput(
                attrs={
                    "class": "block w-full mt-1 text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
                }
            ),
            "is_public": forms.CheckboxInput(
                attrs={"class": "h-4 w-4 text-indigo-600 border-gray-300 rounded"}
            ),
        }


class StockRecordForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # ดึง user ออกจาก kwargs ก่อน
        user = kwargs.pop("user", None)
        # เรียก super() โดยไม่มี user อยู่ใน kwargs แล้ว
        super().__init__(*args, **kwargs)
        # ตอนนี้ค่อยใช้ user เพื่อกรอง queryset
        if user:
            self.fields["partner"].queryset = Partner.objects.filter(user=user)

    class Meta:
        model = StockRecord
        fields = [
            "partner",
            "sku",
            "cost_price",
            "price_excl_tax",
            "price_incl_tax",
            "num_in_stock",
            "low_stock_threshold",
        ]
        widgets = {
            "partner_sku": forms.TextInput(
                attrs={
                    "class": "block w-full mt-1 border-gray-300 rounded-md shadow-sm"
                }
            ),
            "price_excl_tax": forms.NumberInput(
                attrs={
                    "class": "block w-full mt-1 border-gray-300 rounded-md shadow-sm"
                }
            ),
            "num_in_stock": forms.NumberInput(
                attrs={
                    "class": "block w-full mt-1 border-gray-300 rounded-md shadow-sm"
                }
            ),
        }


StockRecordFormSet = inlineformset_factory(
    Product,
    StockRecord,
    form=StockRecordForm,
    extra=1,
    can_delete=False,
    max_num=1,
    fk_name="product",
)

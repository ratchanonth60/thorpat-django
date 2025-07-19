from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class CustomerForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "is_active"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-input w-full"}),
            "email": forms.EmailInput(attrs={"class": "form-input w-full"}),
            "first_name": forms.TextInput(attrs={"class": "form-input w-full"}),
            "last_name": forms.TextInput(attrs={"class": "form-input w-full"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-checkbox"}),
        }
        labels = {
            "username": _("Username"),
            "email": _("Email"),
            "first_name": _("First Name"),
            "last_name": _("Last Name"),
            "is_active": _("Is Active"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ตรวจสอบว่ากำลังแก้ไข User ที่เป็น Superuser/Staff หรือไม่
        # เพื่อป้องกันการเปลี่ยนแปลง is_staff ของตัวเองโดยไม่ได้ตั้งใจผ่านหน้านี้
        if self.instance and self.instance.is_staff:
            if "is_active" in self.fields:
                self.fields["is_active"].help_text = _(
                    "Warning: Changing 'Is Active' for a staff user might affect admin access."
                )

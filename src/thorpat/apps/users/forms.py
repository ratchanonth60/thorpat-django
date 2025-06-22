from django import forms
from django.contrib.auth import forms as admin_forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class CustomPasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        label="Your email address",
        max_length=254,
        widget=forms.EmailInput(attrs={"autocomplete": "email", "class": "..."}),
    )


class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]  # หรือ fields อื่นๆ ที่ต้องการให้อัปเดต
        exclude = [
            "password",
            "username",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
            "last_login",
            "date_joined",
            "is_active",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['email'].widget.attrs['readonly'] = True # ตัวอย่าง: ไม่ให้แก้ไขอีเมล
        for field in self.fields.values():
            field.widget.attrs.update(
                {
                    "class": "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                }
            )


class UserCreationForm(admin_forms.UserCreationForm):
    class Meta(admin_forms.UserCreationForm.Meta):
        model = User
        error_messages = {
            "username": {"unique": _("This username has already been taken.")}
        }


class UserChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):
        model = User

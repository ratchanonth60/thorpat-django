from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


class UserAdmin(BaseUserAdmin):
    # เพิ่ม field ที่ต้องการแสดงใน admin หรือ custom fieldsets
    # ตัวอย่าง: ถ้าต้องการแสดง 'extra_field'
    fieldsets = BaseUserAdmin.fieldsets + ((None, {"fields": ("extra_field",)}),)
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {"fields": ("extra_field",)}),
    )
    list_display = BaseUserAdmin.list_display + ("extra_field",)


admin.site.register(User, UserAdmin)

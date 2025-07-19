import factory
from django.contrib.auth.hashers import make_password
from factory.django import DjangoModelFactory

from thorpat.apps.users.models import User


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User  #

    username = factory.Sequence(lambda n: f"testuser{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    # is_active = True # ใน User model, is_active มีค่า default เป็น True อยู่แล้ว

    # สำหรับ password, เนื่องจาก Django User model ต้องการ password ที่ผ่านการ hash แล้ว
    # เราสามารถใช้ factory.LazyFunction เพื่อสร้าง password ที่ hash แล้วได้
    # หรือจะ override method _create เพื่อใช้ User.objects.create_user() ก็ได้
    password = factory.LazyFunction(lambda: make_password("defaultpassword123"))

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """
        Override _create เพื่อให้แน่ใจว่า password ถูก hash อย่างถูกต้อง
        โดยเฉพาะถ้าไม่ได้ระบุ password มา หรือต้องการใช้ create_user
        """
        manager = cls._get_manager(model_class)
        # ถ้ามีการส่ง password มาใน kwargs และยังไม่ได้ hash
        # ให้ใช้ create_user ซึ่งจะจัดการเรื่องการ hash password เอง
        if "password" in kwargs:
            return manager.create_user(*args, **kwargs)  #
        # ถ้าไม่มี password มา ก็สร้าง user แบบปกติ (อาจจะต้องตั้ง password ทีหลัง)
        return super()._create(model_class, *args, **kwargs)


class ActiveUserFactory(UserFactory):
    is_active = True
    # ไม่จำเป็นต้อง override password ถ้า UserFactory จัดการดีแล้ว


class StaffUserFactory(UserFactory):
    is_staff = True
    is_active = True


class SuperUserFactory(UserFactory):  #
    is_staff = True
    is_superuser = True
    is_active = True

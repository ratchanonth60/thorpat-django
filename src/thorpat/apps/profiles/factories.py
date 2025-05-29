import factory
from factory.django import DjangoModelFactory

from thorpat.apps.profiles.models import Address  #
from thorpat.apps.users.factories import UserFactory


class AddressFactory(DjangoModelFactory):
    class Meta:
        model = Address  #

    user = factory.SubFactory(UserFactory)  # สร้าง User ที่เชื่อมโยงกันโดยอัตโนมัติ
    address_line_1 = factory.Faker("street_address")
    city = factory.Faker("city")
    state_province = factory.Faker("state")
    postal_code = factory.Faker("postcode")
    country = factory.Faker("country_code")  # django-countries ใช้รหัสประเทศ 2 ตัวอักษร
    # phone_number ควรสร้างให้สอดคล้องกับ phonenumber_field และ country
    # ตัวอย่างการสร้าง phone_number ที่อาจจะต้องปรับปรุงให้ถูกต้องตาม format E.164 และประเทศ
    phone_number = factory.LazyAttribute(
        lambda o: f"+1{factory.Faker('msisdn').generate()[-10:]}"  # ตัวอย่างสำหรับ US/Canada
    )
    address_type = factory.Iterator(["Home", "Work", "Shipping", "Billing"])  #
    is_default_shipping = factory.Faker("boolean")
    is_default_billing = factory.Faker("boolean")

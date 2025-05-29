import factory
import phonenumbers
from factory.django import DjangoModelFactory

from thorpat.apps.profiles.models import Address  #
from thorpat.apps.users.factories import UserFactory

_faker = factory.Faker._get_faker()


class AddressFactory(DjangoModelFactory):
    class Meta:
        model = Address  #

    user = factory.SubFactory(UserFactory)
    address_line_1 = factory.Faker("street_address")
    city = factory.Faker("city")
    state_province = factory.Faker("state")
    postal_code = factory.Faker("postcode")
    country = factory.Faker("country_code")  # django-countries ใช้รหัสประเทศ 2 ตัวอักษร

    @factory.lazy_attribute
    def phone_number(self):
        # พยายามสร้างหมายเลขโทรศัพท์ที่ค่อนข้างจะ valid สำหรับประเทศที่ factory สร้างขึ้น
        # นี่เป็น best-effort approach; การ validate เบอร์โทรจริงๆ ซับซ้อนกว่านี้
        # ลองสัก 5 ครั้งเผื่อ Faker สุ่มได้เบอร์ที่ไม่ valid ในครั้งแรกๆ
        for _ in range(5):
            try:
                # ใช้ country.code จาก field 'country' ที่ factory นี้สร้างขึ้น
                # ถ้า self.country เป็น None (ซึ่งไม่ควรเกิดถ้า country field สร้างค่าเสมอ) ให้ default เป็น "US"
                country_code_for_phone = self.country.code if self.country else "US"

                # Faker อาจจะสร้างเบอร์ที่มี extension หรือ format แปลกๆ
                # เราจะพยายาม parse และ format ให้เป็น E.164
                # หมายเหตุ: _faker.phone_number() อาจจะไม่ให้เบอร์ที่ specific กับ region เสมอไป
                # การใช้ provider ที่เจาะจง region ของ Faker อาจจะดีกว่าถ้ามี
                raw_phone_number = _faker.phone_number()

                parsed_number = phonenumbers.parse(
                    raw_phone_number, country_code_for_phone
                )
                if phonenumbers.is_valid_number(parsed_number):
                    return phonenumbers.format_number(
                        parsed_number, phonenumbers.PhoneNumberFormat.E164
                    )
            except phonenumbers.NumberParseException:
                # ถ้า parse ล้มเหลว ให้ลองใหม่ใน loop ถัดไป
                continue
            except Exception:
                # ถ้าเกิด error อื่นๆ ระหว่างการสร้าง ก็ให้ลองใหม่
                continue
        # ถ้าลองหลายครั้งแล้วยังไม่ได้ ให้ใช้ค่า fallback ที่รู้ว่า valid
        return "+16502530000"  # ตัวอย่างเบอร์โทรศัพท์ E.164 ที่ valid (Google US)

    address_type = factory.Iterator(["Home", "Work", "Shipping", "Billing"])  #
    is_default_shipping = factory.Faker("boolean")
    is_default_billing = factory.Faker("boolean")

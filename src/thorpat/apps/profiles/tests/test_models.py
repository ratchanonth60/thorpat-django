from django.test import TestCase

from thorpat.apps.profiles.factories import AddressFactory
from thorpat.apps.profiles.models import Address
from thorpat.apps.users.factories import UserFactory


class AddressModelTests(TestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_create_address(self):
        address = Address.objects.create(
            user=self.user,
            address_line_1="123 Main St",
            city="Anytown",
            postal_code="12345",
            country="US",  # Using country code
            phone_number="+12125552368",
            address_type="Home",
        )
        self.assertEqual(address.user, self.user)
        self.assertEqual(address.address_line_1, "123 Main St")
        self.assertEqual(address.city, "Anytown")
        self.assertEqual(str(address.country), "US")
        self.assertEqual(str(address.phone_number), "+12125552368")
        self.assertEqual(address.address_type, "Home")
        self.assertIsNotNone(address.created_at)
        self.assertIsNotNone(address.updated_at)
        self.assertEqual(
            str(address),
            f"{self.user.username}'s address - 123 Main St, Anytown, United States of America",
        )  # Updated to match __str__

    def test_address_factory(self):
        address = AddressFactory(user=self.user)
        self.assertIsNotNone(address.pk)
        self.assertEqual(address.user, self.user)
        self.assertTrue(Address.objects.filter(pk=address.pk).exists())

    def test_default_shipping_address_behavior(self):
        address1 = AddressFactory(
            user=self.user, is_default_shipping=False, address_type="Ship1"
        )
        address2 = AddressFactory(
            user=self.user, is_default_shipping=True, address_type="Ship2"
        )

        self.assertTrue(Address.objects.get(pk=address2.pk).is_default_shipping)
        self.assertFalse(Address.objects.get(pk=address1.pk).is_default_shipping)

        # Set address1 as default shipping
        address1.is_default_shipping = True
        address1.save()

        self.assertTrue(Address.objects.get(pk=address1.pk).is_default_shipping)
        self.assertFalse(Address.objects.get(pk=address2.pk).is_default_shipping)

        # Ensure only one default shipping address per user
        address3 = AddressFactory(user=self.user, is_default_shipping=True)
        self.assertTrue(Address.objects.get(pk=address3.pk).is_default_shipping)
        self.assertFalse(Address.objects.get(pk=address1.pk).is_default_shipping)
        self.assertFalse(Address.objects.get(pk=address2.pk).is_default_shipping)

    def test_default_billing_address_behavior(self):
        address1 = AddressFactory(
            user=self.user, is_default_billing=False, address_type="Bill1"
        )
        address2 = AddressFactory(
            user=self.user, is_default_billing=True, address_type="Bill2"
        )

        self.assertTrue(Address.objects.get(pk=address2.pk).is_default_billing)
        self.assertFalse(Address.objects.get(pk=address1.pk).is_default_billing)

        # Set address1 as default billing
        address1.is_default_billing = True
        address1.save()

        self.assertTrue(Address.objects.get(pk=address1.pk).is_default_billing)
        self.assertFalse(Address.objects.get(pk=address2.pk).is_default_billing)

        # Ensure only one default billing address per user
        address3 = AddressFactory(user=self.user, is_default_billing=True)
        self.assertTrue(Address.objects.get(pk=address3.pk).is_default_billing)
        self.assertFalse(Address.objects.get(pk=address1.pk).is_default_billing)
        self.assertFalse(Address.objects.get(pk=address2.pk).is_default_billing)

    def test_address_phone_number_validation(self):
        # Assuming phonenumber_field handles most validation,
        # this is a basic check that it's stored.
        # More specific validation tests might be needed if custom logic is added.
        address = AddressFactory(user=self.user, phone_number="+442071838750")
        self.assertEqual(str(address.phone_number), "+442071838750")

    def test_address_country_field(self):
        address = AddressFactory(user=self.user, country="GB")
        self.assertEqual(address.country.code, "GB")
        self.assertEqual(address.country.name, "United Kingdom")

    def test_address_without_optional_fields(self):
        address = Address.objects.create(
            user=self.user,
            address_line_1="Minimal St",
            city="Min City",
            postal_code="00000",
            country="FR",  # Country is required
        )
        self.assertIsNone(address.address_line_2)
        self.assertIsNone(address.state_province)
        self.assertIsNone(address.phone_number)
        self.assertIsNone(address.address_type)
        self.assertFalse(address.is_default_shipping)
        self.assertFalse(address.is_default_billing)

    def test_verbose_name_plural(self):
        self.assertEqual(
            str(Address._meta.verbose_name_plural), "Addresss"
        )  # From 0001_initial.py

    def test_ordering(self):
        AddressFactory(user=self.user)
        AddressFactory(user=self.user)
        addresses = Address.objects.filter(user=self.user)
        # Default ordering is ['-created_at']
        self.assertTrue(addresses[0].created_at > addresses[1].created_at)

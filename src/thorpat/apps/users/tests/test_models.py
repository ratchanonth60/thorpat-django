from django.test import TestCase

from thorpat.apps.users.models import User


class UserModelTests(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpassword123"
        )
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("testpassword123"))
        self.assertTrue(user.is_active)  # is_active is True by default in create_user

    def test_create_superuser(self):
        admin_user = User.objects.create_superuser(
            username="adminuser", email="admin@example.com", password="adminpassword123"
        )
        self.assertEqual(admin_user.username, "adminuser")
        self.assertEqual(admin_user.email, "admin@example.com")
        self.assertTrue(admin_user.check_password("adminpassword123"))
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_active)

    def test_get_full_name(self):
        user = User(first_name="Test", last_name="User")
        self.assertEqual(user.get_full_name(), "Test User")

    def test_get_short_name(self):
        user = User(first_name="Test")
        self.assertEqual(user.get_short_name(), "Test")

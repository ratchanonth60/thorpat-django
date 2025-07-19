from unittest.mock import patch  # For mocking Celery tasks

from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APITestCase

from thorpat.api.v1.utils import token_generator  # Your app's token generator
from thorpat.apps.users.factories import ActiveUserFactory, UserFactory
from thorpat.apps.users.models import User


class AuthAPITests(APITestCase):
    def _assert_response_api_structure(
        self,
        response,
        expected_http_status,
        expected_success_flag,
        expected_message=None,
    ):
        # Helper from previous example, ensure it's available or defined here
        if expected_http_status == status.HTTP_204_NO_CONTENT and not response.content:
            return None  # ไม่มี content ให้เช็ค
        try:
            content = response.json()
            print(f"Response content: {content}")  # Debugging output
        except ValueError:
            self.fail(
                f"Response body is not valid JSON. Status: {response.status_code}, Content: {response.content}"
            )
        self.assertEqual(content["code"], expected_http_status)
        self.assertIn("success", content)
        self.assertEqual(content["success"], expected_success_flag)
        self.assertIn("message", content)
        if expected_message:
            self.assertEqual(content["message"], expected_message)
        self.assertIn("data", content)
        self.assertIn("errors", content)
        return content

    # === User Registration Tests ===
    @patch("thorpat.api.v1.auth.views.send_activation_email_task.delay")
    def test_user_registration_success(self, mock_send_activation_email_task):
        url = reverse("user_register")
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "StrongPassword123!",
            "password2": "StrongPassword123!",
            "first_name": "New",
            "last_name": "User",
        }
        response = self.client.post(url, data, format="json")
        content = self._assert_response_api_structure(
            response, status.HTTP_201_CREATED, True
        )
        self.assertEqual(
            content["message"],
            "User registered successfully. Please check your email to activate your account.",
        )
        self.assertEqual(content["data"]["username"], "newuser")

        user = User.objects.get(username="newuser")
        self.assertFalse(
            user.is_active
        )  # UserRegistrationSerializer creates inactive user
        mock_send_activation_email_task.assert_called_once_with(user.pk)

    def test_user_registration_common_passwords(self):
        url = reverse("user_register")
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "password2": "password456",
        }
        response = self.client.post(url, data, format="json")
        content = self._assert_response_api_structure(
            response, status.HTTP_400_BAD_REQUEST, False
        )
        self.assertIn("password", content["errors"])
        self.assertEqual(
            content["errors"]["password"][0], "This password is too common."
        )

    def test_user_registration_mismatched_passwords(self):
        url = reverse("user_register")
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "054362770aA",
            "password2": "054362770ab",
        }
        response = self.client.post(url, data, format="json")
        content = self._assert_response_api_structure(
            response, status.HTTP_400_BAD_REQUEST, False
        )
        self.assertIn("password", content["errors"])
        self.assertEqual(
            content["errors"]["password"][0], "Password fields didn't match."
        )

    def test_user_registration_existing_username(self):
        UserFactory(username="existinguser", email="someother@email.com")
        url = reverse("user_register")
        data = {
            "username": "existinguser",
            "email": "newemail@example.com",
            "password": "password123",
            "password2": "password123",
        }
        response = self.client.post(url, data, format="json")
        content = self._assert_response_api_structure(
            response, status.HTTP_400_BAD_REQUEST, False
        )
        self.assertIn("username", content["errors"])

    def test_user_registration_existing_email(self):
        UserFactory(username="anotheruser", email="existing@example.com")
        url = reverse("user_register")
        data = {
            "username": "newuser",
            "email": "existing@example.com",
            "password": "password123",
            "password2": "password123",
        }
        response = self.client.post(url, data, format="json")
        content = self._assert_response_api_structure(
            response, status.HTTP_400_BAD_REQUEST, False
        )
        self.assertIn("email", content["errors"])

    # === Account Activation Tests ===
    def test_account_activation_success(self):
        user = UserFactory(is_active=False)  # Created by UserRegistrationSerializer
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)
        url = reverse("account_activate", kwargs={"uidb64": uidb64, "token": token})

        response = self.client.get(url)
        content = self._assert_response_api_structure(
            response,
            status.HTTP_200_OK,
            True,
            "Account activated successfully. You can now login.",
        )
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_account_activation_invalid_token(self):
        user = UserFactory(is_active=False)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        url = reverse(
            "account_activate", kwargs={"uidb64": uidb64, "token": "invalidtoken"}
        )

        response = self.client.get(url)
        self._assert_response_api_structure(
            response,
            status.HTTP_400_BAD_REQUEST,
            False,
            "Activation link is invalid or has expired.",
        )
        user.refresh_from_db()
        self.assertFalse(user.is_active)

    def test_account_activation_already_active(self):
        user = ActiveUserFactory()  # User is already active
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)  # Token might still be valid
        url = reverse("account_activate", kwargs={"uidb64": uidb64, "token": token})

        response = self.client.get(url)
        # The view returns 200 OK if account is already active
        self._assert_response_api_structure(
            response, status.HTTP_200_OK, True, "Account is already active."
        )
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    # === Login Tests (CustomTokenObtainPairView) ===
    def test_login_success(self):
        user = ActiveUserFactory(
            username="loginuser", password="Password123!"
        )  # Ensure password is known
        url = reverse("token_obtain_pair")
        data = {"username": "loginuser", "password": "Password123!"}

        response = self.client.post(url, data, format="json")
        content = self._assert_response_api_structure(
            response, status.HTTP_200_OK, True, "Login successfully"
        )
        self.assertIn("access", content["data"])
        self.assertIn("refresh", content["data"])

    def test_login_inactive_user(self):
        user = UserFactory(
            username="inactiveuser", password="Password123!", is_active=False
        )
        url = reverse("token_obtain_pair")
        data = {"username": "inactiveuser", "password": "Password123!"}

        response = self.client.post(url, data, format="json")
        # Default DRF behavior for inactive user is 401
        content = self._assert_response_api_structure(
            response, status.HTTP_401_UNAUTHORIZED, False
        )
        self.assertIn(
            "detail", content["errors"]
        )  # MyTokenObtainPairSerializer might not be hit if user is inactive
        # This error comes from DRF's auth checks.

    def test_login_invalid_credentials(self):
        ActiveUserFactory(username="loginuser", password="Password123!")
        url = reverse("token_obtain_pair")
        data = {"username": "loginuser", "password": "WrongPassword!"}

        response = self.client.post(url, data, format="json")
        content = self._assert_response_api_structure(
            response, status.HTTP_401_UNAUTHORIZED, False
        )
        self.assertIn("detail", content["errors"])

    # === Password Reset Request Tests ===

    @patch("thorpat.api.v1.auth.views.send_password_reset_email_task.delay")
    def test_password_reset_request_success(self, mock_send_password_reset_email_task):
        user = ActiveUserFactory(email="resetme@example.com")
        url = reverse("password_reset_request")
        data = {"email": "resetme@example.com"}

        response = self.client.post(url, data, format="json")
        self._assert_response_api_structure(
            response,
            status.HTTP_200_OK,
            True,
            "If an account with this email exists, a password reset link has been sent.",
        )
        mock_send_password_reset_email_task.assert_called_once_with(user.pk)

    @patch("thorpat.api.v1.auth.views.send_password_reset_email_task.delay")
    def test_password_reset_request_non_existent_email(
        self, mock_send_password_reset_email_task
    ):
        url = reverse("password_reset_request")
        data = {"email": "nonexistent@example.com"}

        response = self.client.post(url, data, format="json")
        # View should still return 200 OK for security reasons
        self._assert_response_api_structure(
            response,
            status.HTTP_200_OK,
            True,
            "If an account with this email exists, a password reset link has been sent.",
        )
        mock_send_password_reset_email_task.assert_not_called()

    # === Password Reset Confirm Tests ===
    def test_password_reset_confirm_success(self):
        user = ActiveUserFactory(password="OldPassword123!")
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)
        url = reverse("password_reset_confirm")
        data = {
            "uidb64": uidb64,
            "token": token,
            "new_password": "NewStrongPassword123!",
            "new_password2": "NewStrongPassword123!",
        }
        response = self.client.post(url, data, format="json")
        self._assert_response_api_structure(
            response,
            status.HTTP_200_OK,
            True,
            "Password has been reset successfully. You can now login with your new password.",
        )

        user.refresh_from_db()
        self.assertTrue(user.check_password("NewStrongPassword123!"))

    def test_password_reset_confirm_invalid_token(self):
        user = ActiveUserFactory()
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        url = reverse("password_reset_confirm")
        data = {
            "uidb64": uidb64,
            "token": "badtoken",
            "new_password": "NewPassword123!",
            "new_password2": "NewPassword123!",
        }
        response = self.client.post(url, data, format="json")
        content = self._assert_response_api_structure(
            response, status.HTTP_400_BAD_REQUEST, False, "Password reset failed."
        )
        self.assertIn(
            "token", content["errors"]
        )  # PasswordResetConfirmSerializer raises validation error for token

    def test_password_reset_confirm_mismatched_passwords(self):
        user = ActiveUserFactory()
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)
        url = reverse("password_reset_confirm")
        data = {
            "uidb64": uidb64,
            "token": token,
            "new_password": "NewPassword123!",
            "new_password2": "DifferentPassword456!",
        }
        response = self.client.post(url, data, format="json")
        content = self._assert_response_api_structure(
            response, status.HTTP_400_BAD_REQUEST, False, "Password reset failed."
        )
        self.assertIn("new_password", content["errors"])

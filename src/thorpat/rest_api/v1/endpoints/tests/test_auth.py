import json

from django.contrib.auth.hashers import check_password
from django.core import mail
from django.test import Client, TestCase
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from thorpat.apps.users.factories import ActiveUserFactory
from thorpat.apps.users.models import User
from thorpat.rest_api.utils import (
    account_activation_token,
    password_reset_token_generator,
)


class AuthAPITests(TestCase):
    def setUp(self):
        super().setUp()  # ดีถ้ามีการสืบทอด
        self.client = Client()
        self.register_url = "/api/v1/auth/register"
        self.login_url = "/api/v1/auth/login"
        self.confirm_email_base_url = "/api/v1/auth/confirm-email"
        self.password_reset_request_url = "/api/v1/auth/password-reset-request"
        self.password_reset_confirm_url = (
            "/api/v1/auth/password-reset-confirm"  # แก้จาก _base เป็น _url
        )

        # สร้าง active user สำหรับทดสอบการ login และ password reset
        self.raw_password_for_active_user = "FactoryPassword123!"
        self.active_user = ActiveUserFactory(
            username="activefactoryuser",
            password=self.raw_password_for_active_user,  # Factory ควรจะ hash password นี้
        )

        # ข้อมูลตัวอย่างสำหรับส่งใน request body (สำหรับ registration)
        self.user_registration_payload = {
            "username": "newreguser",
            "email": "newreguser@example.com",
            "password": "NewPassword123!",
            "password_confirm": "NewPassword123!",
            "first_name": "NewReg",
            "last_name": "UserReg",
        }

    def test_user_registration_success_and_sends_email(self):
        # ใช้ payload ที่ unique สำหรับ test นี้
        unique_payload = self.user_registration_payload.copy()
        unique_payload["username"] = "unique_user_for_reg_email"
        unique_payload["email"] = "unique_email_for_reg@example.com"

        response = self.client.post(
            self.register_url,
            data=json.dumps(unique_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(
            response_data.get("success"),
            f"Registration failed: {response_data.get('message') or response_data.get('errors')}",
        )
        self.assertEqual(response_data["data"]["username"], unique_payload["username"])
        self.assertFalse(
            response_data["data"]["is_active"]
        )  # User is inactive after registration

        # ตรวจสอบ Email
        self.assertEqual(len(mail.outbox), 1)
        sent_email = mail.outbox[0]
        self.assertEqual(sent_email.subject, "Confirm your Email - Thorpat API")  #
        self.assertIn(unique_payload["email"], sent_email.to)

    def test_user_registration_username_exists(self):
        # สร้าง user ที่มี username ซ้ำกับ active_user ที่สร้างใน setUp
        payload_with_existing_username = self.user_registration_payload.copy()
        payload_with_existing_username["username"] = self.active_user.username
        payload_with_existing_username["email"] = (
            "different_email@example.com"  # email ต้องไม่ซ้ำ
        )

        response = self.client.post(
            self.register_url,
            data=json.dumps(payload_with_existing_username),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)  # Custom handler for HttpError
        response_data = response.json()
        self.assertFalse(response_data["success"])
        self.assertIn("Username already exists", response_data["errors"][0]["message"])

    def test_user_registration_email_exists(self):
        # สร้าง user ที่มี email ซ้ำกับ active_user ที่สร้างใน setUp
        payload_with_existing_email = self.user_registration_payload.copy()
        payload_with_existing_email["username"] = (
            "different_username_for_email_test"  # username ต้องไม่ซ้ำ
        )
        payload_with_existing_email["email"] = self.active_user.email

        response = self.client.post(
            self.register_url,
            data=json.dumps(payload_with_existing_email),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)  # Custom handler for HttpError
        response_data = response.json()
        self.assertFalse(response_data["success"])
        self.assertIn("Email already registered", response_data["errors"][0]["message"])

    def test_user_registration_password_mismatch(self):
        invalid_payload = self.user_registration_payload.copy()
        invalid_payload["password_confirm"] = "wrongpassword"
        response = self.client.post(
            self.register_url,
            data=json.dumps(invalid_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 422)  # Pydantic validation error

    def test_user_login_success_with_factory_user(
        self,
    ):  # ชื่อ test method นี้อาจจะซ้ำซ้อนถ้าทุก user สร้างจาก factory
        login_data = {
            "username": self.active_user.username,
            "password": self.raw_password_for_active_user,  # ใช้ password ดิบที่ใช้สร้าง factory
        }
        response = self.client.post(
            self.login_url, data=json.dumps(login_data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data["success"])
        self.assertIn("access_token", response_data["data"])
        self.assertIn("refresh_token", response_data["data"])

    def test_user_login_inactive_user(self):
        # 1. สร้าง user ที่ inactive โดยใช้ UserFactory (ถ้า UserFactory สร้าง active user by default, ให้ override)
        # หรือลงทะเบียน user ใหม่ ซึ่ง endpoint จะสร้างเป็น inactive
        inactive_user_payload = {
            "username": "inactive_login_test_user",
            "email": "inactive_login_test@example.com",
            "password": "InactivePassword123!",
            "password_confirm": "InactivePassword123!",
        }
        reg_response = self.client.post(
            self.register_url,
            data=json.dumps(inactive_user_payload),
            content_type="application/json",
        )
        self.assertTrue(
            reg_response.json().get("success"),
            "Registration for inactive user test failed",
        )
        # User.objects.get(username=inactive_user_payload["username"]).is_active ควรจะเป็น False

        # 2. พยายาม login ด้วย user ที่ inactive
        login_data_for_inactive = {
            "username": inactive_user_payload["username"],
            "password": inactive_user_payload["password"],
        }
        response = self.client.post(
            self.login_url,
            data=json.dumps(login_data_for_inactive),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)  # HttpError leads to 200
        response_data = response.json()
        self.assertFalse(response_data["success"])

        # ถ้าใช้ default ModelBackend, authenticate จะคืน None สำหรับ inactive user
        self.assertIn(
            "Invalid username or password", response_data["errors"][0]["message"]
        )
        # ถ้าคุณ implement Custom Backend และต้องการให้แสดง "Account not activated":
        # self.assertIn("Account not activated", response_data["errors"][0]["message"].lower())

    def test_email_confirmation_get_link(self):
        # 1. ลงทะเบียน user (จะได้ user ที่ is_active=False)
        user_to_confirm_payload = self.user_registration_payload.copy()
        user_to_confirm_payload["username"] = "user_for_email_confirm"
        user_to_confirm_payload["email"] = "email_confirm@example.com"

        reg_response = self.client.post(
            self.register_url,
            data=json.dumps(user_to_confirm_payload),
            content_type="application/json",
        )
        self.assertTrue(
            reg_response.json().get("success"),
            "Registration for email confirmation test failed",
        )
        user = User.objects.get(username=user_to_confirm_payload["username"])
        self.assertFalse(user.is_active)

        # 2. สร้าง token และ uid
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)

        # 3. เรียก GET endpoint
        confirm_url = f"{self.confirm_email_base_url}/{uid}/{token}"  # Endpoint path
        response = self.client.get(confirm_url)

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data["success"])
        self.assertIn(
            "Email confirmed successfully", response_data["data"]["message"]
        )  # MessageResponseSchema format

        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_password_reset_request_sends_email(self):
        # ใช้ active_user จาก setUp
        payload = {"email": self.active_user.email}
        # Clear outbox ก่อนเรียก API เพื่อให้แน่ใจว่านับอีเมลถูก
        mail.outbox = []
        response = self.client.post(
            self.password_reset_request_url,
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data["success"])
        self.assertIn("password reset link has been sent", response_data["message"])

        self.assertEqual(len(mail.outbox), 1)
        sent_email = mail.outbox[0]
        self.assertEqual(sent_email.subject, "Password Reset Request - Thorpat API")  #
        self.assertIn(self.active_user.email, sent_email.to)

    def test_password_reset_confirm_success(self):
        user_to_reset = self.active_user
        old_password_hash = user_to_reset.password

        uid = urlsafe_base64_encode(force_bytes(user_to_reset.pk))
        token = password_reset_token_generator.make_token(user_to_reset)

        new_password = "NewSecurePasswordConfirm123!"
        confirm_payload = {
            "token": token,
            "new_password": new_password,
            "new_password_confirm": new_password,
        }

        # Endpoint นี้ใช้ uidb64 เป็น query parameter
        target_url = f"{self.password_reset_confirm_url}?uidb64={uid}"
        response = self.client.post(
            target_url,
            data=json.dumps(confirm_payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data["success"])
        self.assertIn("Password has been reset successfully", response_data["message"])

        user_to_reset.refresh_from_db()
        self.assertTrue(check_password(new_password, user_to_reset.password))
        self.assertNotEqual(old_password_hash, user_to_reset.password)

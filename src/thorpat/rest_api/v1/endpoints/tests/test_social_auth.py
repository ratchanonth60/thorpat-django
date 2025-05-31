import json
from unittest.mock import MagicMock, patch

from allauth.socialaccount.models import (
    SocialAccount,
    SocialLogin,
)
from django.test import Client, TestCase

from thorpat.apps.users.factories import UserFactory


class SocialAuthAPITests(TestCase):
    def setUp(self):
        super().setUp()
        self.client = Client()
        self.google_login_url = (
            "/api/v1/social-auth/google/login/"  # หรือใช้ reverse() ถ้าตั้งชื่อ URL
        )

        # ตั้งค่า SocialApp จำลองสำหรับ Google (ถ้าจำเป็น)
        # หรือ mock การ get_provider().get_app()
        # SocialApp.objects.create(
        #     provider='google',
        #     name='Google Test App',
        #     client_id='test_google_client_id',
        #     secret='test_google_secret_key',
        #     # ...
        # )

    @patch(
        "thorpat.rest_api.v1.endpoints.social_auth.GoogleOAuth2Adapter"
    )  # Patch adapter ที่ใช้ใน endpoint ของคุณ
    @patch(
        "thorpat.rest_api.v1.endpoints.social_auth.complete_social_login"
    )  # Patch helper ของ allauth
    @patch("thorpat.rest_api.utils.generate_access_token")  # Patch JWT generation
    @patch("thorpat.rest_api.utils.generate_refresh_token")
    def test_google_login_success_new_user(
        self,
        mock_generate_refresh_token,
        mock_generate_access_token,
        mock_complete_social_login,
        MockGoogleOAuth2Adapter,
    ):
        # --- Setup Mocks ---
        # Mock adapter.complete_login() ที่จะถูกเรียกภายใน endpoint
        mock_adapter_instance = MockGoogleOAuth2Adapter.return_value

        # สร้าง SocialLogin object จำลองที่ adapter.complete_login ควรจะ return
        mock_social_login = SocialLogin()
        mock_social_login.user = None  # จำลองกรณี user ใหม่
        mock_social_login.account = MagicMock(spec=SocialAccount)
        mock_social_login.account.provider = "google"
        mock_social_login.account.uid = "test_google_uid"
        mock_social_login.account.extra_data = {
            "email": "newuser@example.com",
            "given_name": "New",
            "family_name": "User",
        }
        # ... ตั้งค่าอื่นๆ ของ mock_social_login ตามที่ allauth ต้องการ ...

        mock_adapter_instance.complete_login.return_value = mock_social_login

        # Mock complete_social_login() ให้ return user ที่ถูกสร้าง/login
        # และตั้ง request.user
        def side_effect_complete_social_login(request, login_obj):
            # ในสถานการณ์จริง allauth จะสร้าง user และ login
            # ที่นี่เราจำลองว่า user ถูกสร้างและผูกกับ request
            user = UserFactory(
                username="newuser_google", email=login_obj.account.extra_data["email"]
            )
            request.user = user  # สำคัญ: allauth จะ set request.user
            # SocialAccount.objects.create(user=user, provider='google', uid=login_obj.account.uid) # จำลองการสร้าง SocialAccount
            return None  # complete_social_login อาจจะ return HttpResponse หรือ None

        mock_complete_social_login.side_effect = side_effect_complete_social_login

        mock_generate_access_token.return_value = "fake_access_token_for_our_system"
        mock_generate_refresh_token.return_value = "fake_refresh_token_for_our_system"

        # --- Call API ---
        payload = {"access_token": "fake_google_access_token_from_client"}
        response = self.client.post(
            self.google_login_url,
            data=json.dumps(payload),
            content_type="application/json",
        )

        # --- Assertions ---
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        print(response_data)
        self.assertTrue(response_data.get("success"))
        self.assertEqual(response_data.get("message"), "Google login successful")
        self.assertEqual(
            response_data["data"]["access_token"], "fake_access_token_for_our_system"
        )

        # ตรวจสอบว่า user ถูกสร้างใน DB (หรือตาม logic ของ mock_complete_social_login)
        # User.objects.get(email='newuser@example.com')
        # SocialAccount.objects.get(uid='test_google_uid')

        # ตรวจสอบว่า mock ถูกเรียกด้วย arguments ที่ถูกต้อง
        mock_adapter_instance.complete_login.assert_called_once()
        # mock_complete_social_login.assert_called_once() # ตรวจสอบการเรียก

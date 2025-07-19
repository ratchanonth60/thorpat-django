from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from thorpat.apps.users.factories import (
    ActiveUserFactory,
    SuperUserFactory,
)
from thorpat.apps.users.models import User


class UserAPITests(APITestCase):
    def setUp(self):
        self.admin_user = SuperUserFactory()  # Admin user
        self.normal_user1 = ActiveUserFactory(
            username="user1", email="user1@example.com"
        )
        self.normal_user2 = ActiveUserFactory(
            username="user2", email="user2@example.com"
        )

        self.list_create_url = reverse("user-list")  # จาก basename='user'

    def get_detail_url(self, user_id):
        return reverse("user-detail", kwargs={"pk": user_id})

    def _assert_response_api_structure(
        self,
        response,
        expected_http_status,
        expected_success_flag,
        expected_message=None,
    ):
        if expected_http_status == status.HTTP_204_NO_CONTENT and not response.content:
            return None  # ไม่มี content ให้เช็ค
        try:
            content = response.json()
        except ValueError:
            self.fail(
                f"Response body is not valid JSON. Status: {response.status_code}, Content: {response.content}"
            )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "HTTP status code should always be 200 OK.",
        )

        self.assertIn("success", content, "Response missing 'success' key")
        self.assertEqual(
            content["success"],
            expected_success_flag,
            f"'success' flag is not {expected_success_flag}",
        )

        self.assertIn("code", content, "Response missing 'code_status' key")
        self.assertEqual(
            content["code"],
            expected_http_status,
            f"'code_status' in body is not {expected_http_status}",
        )

        self.assertIn("message", content, "Response missing 'message' key")
        if expected_message:
            self.assertEqual(
                content["message"],
                expected_message,
                f"Message mismatch: got '{content['message']}', expected '{expected_message}'",
            )

        self.assertIn("data", content, "Response missing 'data' key")
        self.assertIn("errors", content, "Response missing 'errors' key")

        return content

    # === Test List Users ===

    def test_list_users_as_admin_success(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_create_url)
        content = self._assert_response_api_structure(
            response, status.HTTP_200_OK, True
        )
        # UserView ใช้ pagination
        self.assertIn("results", content["data"])
        # จำนวน user จะขึ้นอยู่กับจำนวนที่สร้าง + admin (3 users ใน setUp)
        self.assertEqual(content["data"]["count"], 3)

    def test_list_users_as_normal_user_permission_denied(self):
        self.client.force_authenticate(user=self.normal_user1)
        response = self.client.get(self.list_create_url)
        self._assert_response_api_structure(response, status.HTTP_403_FORBIDDEN, False)

    def test_list_users_unauthenticated_permission_denied(self):
        response = self.client.get(self.list_create_url)
        self._assert_response_api_structure(
            response, status.HTTP_401_UNAUTHORIZED, False
        )

    # === Test Retrieve User ===
    def test_retrieve_own_user_data_as_normal_user_success(self):
        self.client.force_authenticate(user=self.normal_user1)
        url = self.get_detail_url(self.normal_user1.id)
        response = self.client.get(url)
        content = self._assert_response_api_structure(
            response, status.HTTP_200_OK, True
        )
        self.assertEqual(content["data"]["id"], self.normal_user1.id)
        self.assertEqual(content["data"]["username"], self.normal_user1.username)

    def test_retrieve_other_user_data_as_normal_user_permission_denied(self):
        # สมมติว่า normal user ไม่มีสิทธิ์ดูข้อมูล user อื่น (ยกเว้น admin)
        self.client.force_authenticate(user=self.normal_user1)
        url = self.get_detail_url(self.normal_user2.id)
        response = self.client.get(url)
        self._assert_response_api_structure(
            response, status.HTTP_403_FORBIDDEN, False
        )  # หรือ 404 ถ้า filter queryset

    def test_retrieve_any_user_data_as_admin_success(self):
        self.client.force_authenticate(user=self.admin_user)
        url = self.get_detail_url(self.normal_user1.id)
        response = self.client.get(url)
        content = self._assert_response_api_structure(
            response, status.HTTP_200_OK, True
        )
        self.assertEqual(content["data"]["id"], self.normal_user1.id)

    # === Test Update User (PATCH) ===
    def test_update_own_user_data_patch_as_normal_user_success(self):
        self.client.force_authenticate(user=self.normal_user1)
        url = self.get_detail_url(self.normal_user1.id)
        patch_data = {"first_name": "UpdatedFirstName", "last_name": "UpdatedLastName"}
        response = self.client.patch(url, patch_data, format="json")
        content = self._assert_response_api_structure(
            response, status.HTTP_200_OK, True
        )
        self.assertEqual(content["data"]["first_name"], "UpdatedFirstName")
        self.normal_user1.refresh_from_db()
        self.assertEqual(self.normal_user1.first_name, "UpdatedFirstName")

    def test_update_other_user_data_patch_as_normal_user_permission_denied(self):
        self.client.force_authenticate(user=self.normal_user1)
        url = self.get_detail_url(self.normal_user2.id)
        patch_data = {"first_name": "TryingToUpdate"}
        response = self.client.patch(url, patch_data, format="json")
        self._assert_response_api_structure(
            response, status.HTTP_403_FORBIDDEN, False
        )  # หรือ 404

    def test_update_any_user_data_patch_as_admin_success(self):
        self.client.force_authenticate(user=self.admin_user)
        url = self.get_detail_url(self.normal_user1.id)
        patch_data = {"is_staff": True}
        response = self.client.patch(url, patch_data, format="json")
        content = self._assert_response_api_structure(
            response, status.HTTP_200_OK, True
        )
        self.assertTrue(content["data"]["is_staff"])
        self.normal_user1.refresh_from_db()
        self.assertTrue(self.normal_user1.is_staff)

    def test_update_user_username_or_email_validation(self):
        self.client.force_authenticate(user=self.admin_user)
        # user2's email is user2@example.com
        url = self.get_detail_url(self.normal_user1.id)
        patch_data = {
            "email": self.normal_user2.email
        }  # พยายามเปลี่ยน email ของ user1 ให้เหมือน user2
        response = self.client.patch(url, patch_data, format="json")

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )  # หรือ status code ที่คุณคาดหวัง
        content = self._assert_response_api_structure(
            response, status.HTTP_400_BAD_REQUEST, False
        )
        self.assertIn("email", content["errors"])  # หรือ 'detail' หรือ key ที่เหมาะสม

    # === Test Delete User (Admin only) ===
    def test_delete_user_as_admin_success(self):
        self.client.force_authenticate(user=self.admin_user)
        user_to_delete_id = self.normal_user1.id
        url = self.get_detail_url(user_to_delete_id)
        response = self.client.delete(url)
        self._assert_response_api_structure(response, status.HTTP_204_NO_CONTENT, True)
        self.assertFalse(User.objects.filter(id=user_to_delete_id).exists())

    def test_delete_user_as_normal_user_permission_denied(self):
        self.client.force_authenticate(user=self.normal_user1)
        url = self.get_detail_url(self.normal_user2.id)
        response = self.client.delete(url)
        self._assert_response_api_structure(response, status.HTTP_204_NO_CONTENT, False)

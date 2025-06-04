from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from thorpat.apps.profiles.factories import AddressFactory
from thorpat.apps.profiles.models import Address
from thorpat.apps.users.factories import (
    ActiveUserFactory,
)


class AddressAPITests(APITestCase):
    def setUp(self):
        # สร้าง users สำหรับ test
        self.user1 = ActiveUserFactory()
        self.user2 = ActiveUserFactory()

        # สร้าง address สำหรับ user1
        self.address1_user1 = AddressFactory(user=self.user1)
        self.address2_user1 = AddressFactory(user=self.user1)

        # สร้าง address สำหรับ user2
        self.address1_user2 = AddressFactory(user=self.user2)

        # URL endpoints
        self.list_create_url = reverse(
            "address-list"
        )  # จาก basename='address' ใน routers.py
        self.detail_url_template = "address-detail"  # สำหรับ reverse ด้านใน test method

    def get_detail_url(self, address_id):
        return reverse(self.detail_url_template, kwargs={"pk": address_id})

    # Helper method สำหรับตรวจสอบโครงสร้าง ResponseAPI
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
        self.assertEqual(content["code"], expected_http_status)

        self.assertIn("success", content, "Response missing 'success' key")
        self.assertEqual(
            content["success"],
            expected_success_flag,
            f"'success' flag is not {expected_success_flag}",
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

    # --- Test List Addresses (GET /api/v1/profiles/addresses/) ---
    def test_list_addresses_authenticated_returns_own_addresses(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.list_create_url)

        content = self._assert_response_api_structure(
            response, status.HTTP_200_OK, True
        )

        # ตรวจสอบ pagination (ถ้ามี)
        # DEFAULT_PAGINATION_CLASS คือ PageNumberPagination, PAGE_SIZE = 10
        self.assertIn(
            "results", content["data"], "Paginated data should have 'results' key"
        )
        self.assertEqual(
            content["data"]["count"], 2, "Should list 2 addresses for user1"
        )
        self.assertEqual(len(content["data"]["results"]), 2)

        retrieved_ids = {item["id"] for item in content["data"]["results"]}
        self.assertIn(self.address1_user1.id, retrieved_ids)
        self.assertIn(self.address2_user1.id, retrieved_ids)
        self.assertNotIn(
            self.address1_user2.id,
            retrieved_ids,
            "Should not list other user's addresses",
        )

    def test_list_addresses_unauthenticated_returns_401(self):
        response = self.client.get(self.list_create_url)
        content = self._assert_response_api_structure(
            response, status.HTTP_401_UNAUTHORIZED, False
        )
        self.assertIsNotNone(content["errors"])
        self.assertIn("detail", content["errors"])

    # --- Test Create Address (POST /api/v1/profiles/addresses/) ---
    def test_create_address_authenticated_success(self):
        self.client.force_authenticate(user=self.user1)
        address_data = {
            "address_line_1": "123 New Street",
            "city": "New City",
            "postal_code": "N3W C1T",
            "country": "US",  # ส่งเป็น country code
            "phone_number": "+12025550104",
            "address_type": "Home Office",
        }
        response = self.client.post(self.list_create_url, address_data, format="json")
        content = self._assert_response_api_structure(
            response, status.HTTP_201_CREATED, True
        )

        self.assertIsNotNone(content["data"])
        new_address_id = content["data"]["id"]
        self.assertEqual(
            content["data"]["address_line_1"], address_data["address_line_1"]
        )
        self.assertEqual(content["data"]["city"], address_data["city"])
        # AddressSerializer คืน country เป็น dict
        self.assertEqual(content["data"]["country"]["code"], address_data["country"])
        self.assertTrue(
            Address.objects.filter(id=new_address_id, user=self.user1).exists()
        )

    def test_create_address_missing_required_fields_returns_400(self):
        self.client.force_authenticate(user=self.user1)
        invalid_data = {
            "city": "A City Without Street"
        }  # ขาด address_line_1, postal_code, country
        response = self.client.post(self.list_create_url, invalid_data, format="json")
        content = self._assert_response_api_structure(
            response, status.HTTP_400_BAD_REQUEST, False
        )

        self.assertIsNotNone(content["errors"])
        self.assertIn("address_line_1", content["errors"])
        self.assertIn("postal_code", content["errors"])
        self.assertIn("country", content["errors"])

    def test_create_address_unauthenticated_returns_401(self):
        address_data = {
            "address_line_1": "123 Sneaky St",
            "city": "NoAuthCity",
            "postal_code": "NA1 NA1",
            "country": "GB",
        }
        response = self.client.post(self.list_create_url, address_data, format="json")
        self._assert_response_api_structure(
            response, status.HTTP_401_UNAUTHORIZED, False
        )

    # --- Test Retrieve Address (GET /api/v1/profiles/addresses/{id}/) ---
    def test_retrieve_own_address_authenticated_success(self):
        self.client.force_authenticate(user=self.user1)
        url = self.get_detail_url(self.address1_user1.id)
        response = self.client.get(url)
        content = self._assert_response_api_structure(
            response, status.HTTP_200_OK, True
        )

        self.assertIsNotNone(content["data"])
        self.assertEqual(content["data"]["id"], self.address1_user1.id)
        self.assertEqual(
            content["data"]["address_line_1"], self.address1_user1.address_line_1
        )

    def test_retrieve_other_user_address_returns_404(self):
        self.client.force_authenticate(user=self.user1)
        url = self.get_detail_url(self.address1_user2.id)  # พยายามดู address ของ user2
        response = self.client.get(url)
        # IsOwner permission และ queryset filtering จะทำให้ไม่เจอ object นี้สำหรับ user1
        self._assert_response_api_structure(response, status.HTTP_404_NOT_FOUND, False)

    def test_retrieve_address_unauthenticated_returns_401(self):
        url = self.get_detail_url(self.address1_user1.id)
        response = self.client.get(url)
        self._assert_response_api_structure(
            response, status.HTTP_401_UNAUTHORIZED, False
        )

    # --- Test Update Address (PUT /api/v1/profiles/addresses/{id}/) ---
    def test_update_own_address_put_authenticated_success(self):
        self.client.force_authenticate(user=self.user1)
        url = self.get_detail_url(self.address1_user1.id)
        update_data = {
            "address_line_1": "Completely Updated Street",
            "address_line_2": "Suite 100",
            "city": "Updated City",
            "state_province": "UP",
            "postal_code": "U1P D8T",
            "country": "CA",
            "phone_number": "+16135550120",
            "address_type": "Primary Residence",
        }
        response = self.client.put(url, update_data, format="json")
        content = self._assert_response_api_structure(
            response, status.HTTP_200_OK, True
        )

        self.assertEqual(
            content["data"]["address_line_1"], update_data["address_line_1"]
        )
        self.assertEqual(content["data"]["city"], update_data["city"])
        self.address1_user1.refresh_from_db()
        self.assertEqual(self.address1_user1.city, update_data["city"])

    def test_update_other_user_address_put_returns_404(self):
        self.client.force_authenticate(user=self.user1)
        url = self.get_detail_url(self.address1_user2.id)
        update_data = {
            "address_line_1": "Trying to takeover",
            "city": "Evil City",
            "postal_code": "E1V 1L1",
            "country": "US",
        }
        response = self.client.put(url, update_data, format="json")
        self._assert_response_api_structure(response, status.HTTP_404_NOT_FOUND, False)

    # --- Test Partial Update Address (PATCH /api/v1/profiles/addresses/{id}/) ---
    def test_partial_update_own_address_patch_authenticated_success(self):
        self.client.force_authenticate(user=self.user1)
        original_address_line_1 = self.address1_user1.address_line_1
        url = self.get_detail_url(self.address1_user1.id)
        patch_data = {"city": "Partially Updated City"}

        response = self.client.patch(url, patch_data, format="json")
        content = self._assert_response_api_structure(
            response, status.HTTP_200_OK, True
        )

        self.assertEqual(content["data"]["city"], patch_data["city"])
        self.address1_user1.refresh_from_db()
        self.assertEqual(self.address1_user1.city, patch_data["city"])
        self.assertEqual(
            self.address1_user1.address_line_1,
            original_address_line_1,
            "Non-patched fields should remain unchanged",
        )

    # --- Test Delete Address (DELETE /api/v1/profiles/addresses/{id}/) ---
    def test_delete_own_address_authenticated_success(self):
        self.client.force_authenticate(user=self.user1)
        address_id_to_delete = self.address1_user1.id
        url = self.get_detail_url(address_id_to_delete)

        response = self.client.delete(url)

        # ModelViewSet.destroy() returns HTTP_204_NO_CONTENT by default.
        # If your CustomAPIRenderer and/or ResponseAPI always generate a body,
        # the status code might be 204 with a body, or transformed to 200.
        # Assuming CustomAPIRenderer will provide a body based on ResponseAPI structure even for 204.
        content = self._assert_response_api_structure(
            response, status.HTTP_204_NO_CONTENT, True
        )

        # If it's 204, content might be None if _assert_response_api_structure handles it.
        if content:  # if there's a body (e.g., CustomAPIRenderer added one)
            self.assertIsNone(
                content["data"], "Data should be null for successful delete"
            )

        self.assertFalse(Address.objects.filter(id=address_id_to_delete).exists())

    def test_delete_other_user_address_returns_404(self):
        self.client.force_authenticate(user=self.user1)
        url = self.get_detail_url(self.address1_user2.id)
        response = self.client.delete(url)
        self._assert_response_api_structure(response, status.HTTP_404_NOT_FOUND, False)

    def test_delete_address_unauthenticated_returns_401(self):
        url = self.get_detail_url(self.address1_user1.id)
        response = self.client.delete(url)
        self._assert_response_api_structure(
            response, status.HTTP_401_UNAUTHORIZED, False
        )

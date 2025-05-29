import json
from django.test import Client, TestCase

from thorpat.apps.users.factories import ActiveUserFactory
from thorpat.apps.profiles.factories import AddressFactory
from thorpat.apps.profiles.models import Address


class ProfileAPITests(TestCase):
    def setUp(self):
        super().setUp()
        self.client = Client()

        # URLs
        self.addresses_url = "/api/v1/profiles/addresses/"  # Adjusted to match routing

        # Create and login user
        self.raw_password = "TestPassword123!"
        self.user = ActiveUserFactory(
            username="profileuser", password=self.raw_password
        )

        login_payload = {
            "username": self.user.username,
            "password": self.raw_password,
        }
        # Assuming your login URL is /api/v1/auth/login
        login_response = self.client.post(
            "/api/v1/auth/login",
            data=json.dumps(login_payload),
            content_type="application/json",
        )
        self.assertEqual(
            login_response.status_code, 200, "Login failed in setUp for profile user"
        )
        login_data = login_response.json()
        self.assertTrue(
            login_data.get("success"), "Login response was not successful in setUp"
        )
        self.access_token = login_data["data"]["access_token"]
        self.auth_headers = {"HTTP_AUTHORIZATION": f"Bearer {self.access_token}"}

        # Create an address for the user for retrieval/update/delete tests
        self.address = AddressFactory(user=self.user, city="Testville")

    def _get_address_detail_url(self, address_id):
        # Helper to construct detail URL dynamically if needed, or use fixed string
        return f"{self.addresses_url}{address_id}/"  #

    def test_create_address_success(self):
        payload = {
            "address_line_1": "1 New Street",
            "city": "New City",
            "postal_code": "52130",
            "country": "TH",  #
            "phone_number": "+66631146861",  #
            "address_type": "Work",  #
            "is_default_shipping": True,  #
        }
        response = self.client.post(
            self.addresses_url,
            data=json.dumps(payload),
            content_type="application/json",
            **self.auth_headers,
        )
        self.assertEqual(response.status_code, 200)  # API returns 200 on success
        response_data = response.json()
        print(response_data)  # Debugging output
        self.assertTrue(response_data["success"])
        self.assertEqual(response_data["message"], "Address created successfully.")  #
        self.assertEqual(response_data["data"]["address_line_1"], "1 New Street")
        self.assertEqual(response_data["data"]["city"], "New City")
        self.assertTrue(response_data["data"]["is_default_shipping"])

        # Verify it's in the database and linked to the user
        self.assertTrue(
            Address.objects.filter(
                user=self.user, address_line_1="1 New Street"
            ).exists()
        )

    def test_create_address_invalid_phone_number_format(self):
        payload = {
            "address_line_1": "123 Phone Test St",
            "city": "Phonetown",
            "postal_code": "12345",
            "country": "US",
            "phone_number": "invalid-phone-number-format",  # Invalid format
            "address_type": "Test",
        }
        response = self.client.post(
            self.addresses_url,
            data=json.dumps(payload),
            content_type="application/json",
            **self.auth_headers,
        )
        self.assertEqual(response.status_code, 200)  # Custom handler changes status
        response_data = response.json()
        self.assertFalse(response_data["success"])
        # Check the generic top-level message
        self.assertEqual(
            response_data.get("message"),
            "Validation failed. Please check your input.",
        )

        # The specific error message comes from the AddressCreateSchema validator
        # and should be in the "errors" list.
        self.assertTrue(
            isinstance(response_data.get("errors"), list),
            "Errors field is not a list.",
        )
        self.assertGreater(
            len(response_data.get("errors", [])), 0, "Errors list is empty."
        )

        found_phone_error = False
        for error_detail in response_data.get("errors", []):
            if error_detail.get("field") == "phone_number":
                # The AddressCreateSchema validator for phone_number raises:
                # ValueError("Invalid phone number format.") or
                # ValueError("The phone number entered is not valid.") or
                # ValueError(f"Could not process phone number: {e}")
                # We'll check if the message contains the expected phrase.
                # The exact message from Pydantic for the AddressCreateSchema is "Invalid phone number format."
                # when phonenumbers.NumberParseException occurs.
                if "Invalid phone number format." in error_detail.get("message", ""):
                    found_phone_error = True
                    break
        self.assertTrue(
            found_phone_error,
            "Specific 'Invalid phone number format.' error for 'phone_number' field not found in error details. "
            f"Actual errors: {response_data.get('errors')}",
        )

    def test_create_address_invalid_phone_number_format(self):
        payload = {
            "address_line_1": "123 Phone Test St",
            "city": "Phonetown",
            "postal_code": "12345",
            "country": "US",
            "phone_number": "invalid-phone-number-format",  # Invalid format
            "address_type": "Test",
        }
        response = self.client.post(
            self.addresses_url,
            data=json.dumps(payload),
            content_type="application/json",
            **self.auth_headers,
        )
        self.assertEqual(response.status_code, 200)  # Custom handler changes status
        response_data = response.json()
        self.assertFalse(response_data["success"])
        # The error message comes from the AddressCreateSchema validator
        self.assertIn("Validation failed.", response_data.get("message", ""))

    def test_retrieve_address_success(self):
        url = self._get_address_detail_url(self.address.id)
        response = self.client.get(url, **self.auth_headers)
        self.assertEqual(response.status_code, 200)  #
        response_data = response.json()
        self.assertTrue(response_data["success"])
        self.assertEqual(response_data["data"]["id"], self.address.id)
        self.assertEqual(response_data["data"]["city"], self.address.city)

    def test_retrieve_address_not_found(self):
        non_existent_id = self.address.id + 999
        url = self._get_address_detail_url(non_existent_id)
        response = self.client.get(url, **self.auth_headers)
        self.assertEqual(
            response.status_code, 200
        )  # get_object_or_404 raises Http404, custom handler returns 200
        response_data = response.json()
        self.assertFalse(response_data["success"])
        self.assertIn(
            "No Address matches the given query.", response_data["errors"][0]["message"]
        )

    def test_retrieve_address_forbidden_for_other_user(self):
        other_user = ActiveUserFactory(
            username="otherprofileuser", password="otherpassword"
        )
        other_user_address = AddressFactory(user=other_user, city="SecretCity")

        url = self._get_address_detail_url(other_user_address.id)
        response = self.client.get(url, **self.auth_headers)  # Using self.user's token

        # The endpoint uses get_object_or_404(Address, id=address_id, user=request.user)
        # This will result in a 404 if the address belongs to another user
        self.assertEqual(response.status_code, 200)  # Custom handler returns 200
        response_data = response.json()
        self.assertFalse(response_data["success"])
        self.assertIn(
            "No Address matches the given query.", response_data["errors"][0]["message"]
        )

    def test_update_address_success(self):
        url = self._get_address_detail_url(self.address.id)
        payload = {
            "city": "UpdatedCityville",
            "is_default_billing": True,  #
        }
        response = self.client.put(
            url,
            data=json.dumps(payload),
            content_type="application/json",
            **self.auth_headers,
        )
        self.assertEqual(response.status_code, 200)  #
        response_data = response.json()
        print(response_data)  # Debugging output
        self.assertTrue(response_data["success"])
        self.assertEqual(response_data["message"], "Address updated successfully.")  #
        self.assertEqual(response_data["data"]["city"], "UpdatedCityville")
        self.assertTrue(response_data["data"]["is_default_billing"])

        self.address.refresh_from_db()
        self.assertEqual(self.address.city, "UpdatedCityville")
        self.assertTrue(self.address.is_default_billing)

    def test_update_address_partial_update(self):
        url = self._get_address_detail_url(self.address.id)
        original_line1 = self.address.address_line_1
        payload = {"postal_code": "99999"}  # Only updating postal code
        response = self.client.put(
            url,
            data=json.dumps(payload),
            content_type="application/json",
            **self.auth_headers,
        )
        self.assertEqual(response.status_code, 200)  #
        response_data = response.json()
        print(response_data)  # Debugging output
        self.assertTrue(response_data["success"])
        self.assertEqual(response_data["data"]["postal_code"], "99999")
        self.assertEqual(
            response_data["data"]["address_line_1"], original_line1
        )  # Check other fields remain

        self.address.refresh_from_db()
        self.assertEqual(self.address.postal_code, "99999")
        self.assertEqual(self.address.address_line_1, original_line1)

    def test_delete_address_success(self):
        address_to_delete = AddressFactory(user=self.user, city="DeleteMeCity")
        url = self._get_address_detail_url(address_to_delete.id)

        response = self.client.delete(url, **self.auth_headers)
        self.assertEqual(response.status_code, 200)  #
        response_data = response.json()
        self.assertTrue(response_data["success"])
        self.assertEqual(response_data["message"], "Address deleted successfully.")  #

        self.assertFalse(Address.objects.filter(pk=address_to_delete.id).exists())

    def test_delete_address_not_found(self):
        non_existent_id = self.address.id + 998
        url = self._get_address_detail_url(non_existent_id)
        response = self.client.delete(url, **self.auth_headers)
        self.assertEqual(response.status_code, 200)  # Custom handler returns 200
        response_data = response.json()
        self.assertFalse(response_data["success"])
        self.assertIn(
            "No Address matches the given query.", response_data["errors"][0]["message"]
        )

    def test_unauthenticated_access_to_profiles_endpoints(self):
        # Test POST
        payload = {
            "address_line_1": "1 Unauth St",
            "city": "Unauth City",
            "postal_code": "000",
            "country": "UA",
        }
        response_post = self.client.post(
            self.addresses_url,
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response_post.status_code, 200)  # Custom auth error handler
        self.assertFalse(response_post.json()["success"])
        self.assertIn("Unauthorized", response_post.json()["errors"][0]["message"])

        # Test GET detail
        detail_url = self._get_address_detail_url(self.address.id)
        response_get_detail = self.client.get(detail_url)
        self.assertEqual(
            response_get_detail.status_code, 200
        )  # Custom auth error handler
        self.assertFalse(response_get_detail.json()["success"])
        self.assertIn(
            "Unauthorized", response_get_detail.json()["errors"][0]["message"]
        )

        # Test PUT
        response_put = self.client.put(
            detail_url,
            data=json.dumps({"city": "TryUpdateUnauth"}),
            content_type="application/json",
        )
        self.assertEqual(response_put.status_code, 200)  # Custom auth error handler
        self.assertFalse(response_put.json()["success"])
        self.assertIn("Unauthorized", response_put.json()["errors"][0]["message"])

        # Test DELETE
        response_delete = self.client.delete(detail_url)
        self.assertEqual(response_delete.status_code, 200)  # Custom auth error handler
        self.assertFalse(response_delete.json()["success"])
        self.assertIn("Unauthorized", response_delete.json()["errors"][0]["message"])

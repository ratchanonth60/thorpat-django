import json

from django.test import Client, TestCase

from thorpat.apps.users.factories import ActiveUserFactory, UserFactory
from thorpat.apps.users.models import User


class UserAPITests(TestCase):
    def setUp(self):
        super().setUp()
        self.client = Client()

        # URLs
        self.users_url = "/api/v1/users/"
        self.me_url = "/api/v1/users/me/"

        # สร้าง users สำหรับ test
        self.raw_password = "TestPassword123!"
        self.normal_user = ActiveUserFactory(
            username="normaluser", password=self.raw_password
        )
        self.another_user = ActiveUserFactory(
            username="anotheruser", password="anotherpassword"
        )
        # self.staff_user = StaffUserFactory(username="staffuser", password="staffpassword") # ถ้ามี endpoint ที่ต้องการ staff

        # Login normal_user เพื่อเอา token (สำหรับ tests ส่วนใหญ่)
        login_payload = {
            "username": self.normal_user.username,
            "password": self.raw_password,
        }
        response = self.client.post(
            "/api/v1/auth/login",
            data=json.dumps(login_payload),
            content_type="application/json",
        )
        self.assertEqual(
            response.status_code, 200, "Login failed in setUp for normal_user"
        )
        login_data = response.json()
        self.assertTrue(
            login_data.get("success"), "Login response was not successful in setUp"
        )
        self.access_token = login_data["data"]["access_token"]
        self.auth_headers = {"HTTP_AUTHORIZATION": f"Bearer {self.access_token}"}

        # (ทางเลือก) Login staff_user เพื่อเอา token สำหรับ staff-only tests
        # staff_login_payload = {"username": self.staff_user.username, "password": "staffpassword"}
        # staff_response = self.client.post("/api/v1/auth/login", data=json.dumps(staff_login_payload), content_type="application/json")
        # self.staff_access_token = staff_response.json()["data"]["access_token"]
        # self.staff_auth_headers = {"HTTP_AUTHORIZATION": f"Bearer {self.staff_access_token}"}

    def test_get_current_user_me(self):
        response = self.client.get(self.me_url, **self.auth_headers)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data["success"])
        self.assertEqual(response_data["data"]["username"], self.normal_user.username)
        self.assertEqual(response_data["data"]["email"], self.normal_user.email)
        # ตรวจสอบ fields อื่นๆ ตาม UserSchema

    def test_update_current_user_me(self):
        update_payload = {
            "first_name": "UpdatedFirstName",
            "last_name": "UpdatedLastName",
        }
        response = self.client.put(
            self.me_url,
            data=json.dumps(update_payload),
            content_type="application/json",
            **self.auth_headers,
        )
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data["success"])
        self.assertEqual(response_data["data"]["first_name"], "UpdatedFirstName")
        self.assertEqual(response_data["data"]["last_name"], "UpdatedLastName")

        # ตรวจสอบว่าข้อมูลใน database อัปเดตจริง
        self.normal_user.refresh_from_db()
        self.assertEqual(self.normal_user.first_name, "UpdatedFirstName")
        self.assertEqual(self.normal_user.last_name, "UpdatedLastName")

    def test_get_users_list_paginated_and_filtered(self):
        # สร้าง user เพิ่มเติมสำหรับทดสอบ pagination และ filter
        ActiveUserFactory(
            username="filteruserA",
            first_name="Alpha",
            email="alpha_filter@example.com",
            password="password",
        )
        ActiveUserFactory(
            username="filteruserB",
            first_name="Beta",
            email="beta_common@example.com",
            password="password",
        )
        UserFactory(
            username="inactive_user_list", is_active=False, password="password"
        )  # User ที่ inactive

        # Test 1: Get first page, default per_page (10)
        response = self.client.get(self.users_url, **self.auth_headers)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()[
            "data"
        ]  # Endpoint users.py คืน BaseResponse[PaginatedDataBase[UserSchema]]

        # จำนวน user ทั้งหมดที่ is_active=True (default filter)
        # self.normal_user, self.another_user, filteruserA, filteruserB = 4 active users
        total_active_users = User.objects.filter(is_active=True).count()
        self.assertEqual(response_data["total_items"], total_active_users)
        self.assertTrue(len(response_data["items"]) <= 10)  # Default per_page

        # Test 2: Pagination
        response = self.client.get(
            f"{self.users_url}?page=1&per_page=2", **self.auth_headers
        )
        self.assertEqual(response.status_code, 200)
        response_data_page1 = response.json()["data"]
        self.assertEqual(len(response_data_page1["items"]), 2)
        self.assertEqual(response_data_page1["current_page"], 1)
        if total_active_users > 2:
            self.assertTrue(response_data_page1["has_next"])
        else:
            self.assertFalse(response_data_page1["has_next"])

        # Test 3: Filtering (ตัวอย่าง: filter by first_name)
        # UserFilterSchema มี first_name__icontains
        response = self.client.get(
            f"{self.users_url}?first_name=Alpha", **self.auth_headers
        )
        self.assertEqual(response.status_code, 200)
        response_data_filtered = response.json()["data"]
        self.assertEqual(response_data_filtered["total_items"], 1)
        self.assertEqual(response_data_filtered["items"][0]["first_name"], "Alpha")

        # Test 4: Filtering for inactive users (UserFilterSchema มี is_active field)
        response = self.client.get(
            f"{self.users_url}?is_active=false", **self.auth_headers
        )
        self.assertEqual(response.status_code, 200)
        response_data_inactive = response.json()["data"]
        self.assertEqual(
            response_data_inactive["total_items"],
            User.objects.filter(is_active=False).count(),
        )

    def test_get_user_by_id_success(self):
        # normal_user (ที่ login อยู่) ดึงข้อมูล another_user
        # Endpoint /users/{user_id}/ ไม่มีการ check staff ในโค้ดปัจจุบัน
        # ถ้ามีการเพิ่ม logic staff check, test นี้อาจจะต้องใช้ staff_auth_headers
        target_user_url = f"{self.users_url}{self.another_user.id}/"
        response = self.client.get(target_user_url, **self.auth_headers)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data["success"])
        self.assertEqual(response_data["data"]["username"], self.another_user.username)

    def test_get_user_by_id_not_found(self):
        non_existent_user_id = User.objects.latest("id").id + 999  # ID ที่ไม่มีอยู่จริง
        target_user_url = f"{self.users_url}{non_existent_user_id}/"
        response = self.client.get(target_user_url, **self.auth_headers)
        # get_object_or_404 จะ raise Http404, ซึ่ง Ninja จะ map ไปเป็น HttpError(404)
        # Custom handler จะเปลี่ยนเป็น status 200 พร้อม error message
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertFalse(response_data["success"])
        self.assertIn(
            "No User matches the given query.", response_data["errors"][0]["message"]
        )  # Default message from get_object_or_404

    # เพิ่ม test cases สำหรับ authentication (ถ้า user ไม่ได้ login จะต้องได้ 401 หรือตาม custom handler)
    def test_get_me_unauthenticated(self):
        response = self.client.get(self.me_url)  # ไม่ใส่ auth_headers
        self.assertEqual(response.status_code, 200)  # AuthenticationError handler
        response_data = response.json()
        self.assertFalse(response_data["success"])
        self.assertIn(
            "Unauthorized", response_data["errors"][0]["message"]
        )  # Default message from HttpBearer

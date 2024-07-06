from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework import status


USER_URL = reverse("users_service:registration")


class UserModelTestCase(TestCase):

    def test_create_user_with_login(self):
        data = {
            "username": "test",
            "password": "test password",
        }
        response = self.client.post(USER_URL, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_with_email(self):
        data = {
            "password": "test password",
            "email": "test@mail.com",
        }
        response = self.client.post(USER_URL, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

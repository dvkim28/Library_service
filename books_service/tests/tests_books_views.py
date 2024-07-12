from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from books_service.models import Book
from users_service.models import User

BOOKS_LIST_VIEW = reverse('books_service:book-list')
BOOKS_RETRIEVE_VIEW = reverse('books_service:book-detail', kwargs={'pk': 1})


def sample_book(**params):
    default = {
        "title": "Test Book",
        "author": "Test Author",
        "cover": "Soft",
        "inventory": 10,
        "daily_fee": 10,
    }
    default.update(params)
    return Book.objects.create(**default)


def get_book_retrieve(book_id):
    return reverse('books_service:book-detail', kwargs={'pk': book_id})


class UnAuthorizedBookRetrieveAPITestCase(APITestCase):
    def setUp(self):
        self.book = sample_book()
        self.client = APIClient()
        self.client.force_authenticate(user=None)

    def test_unauthorized_book_retrieve(self):
        url = get_book_retrieve(self.book.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthorized_book_list(self):
        response = self.client.get(BOOKS_LIST_VIEW)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AuthorizedBookRetrieveAPITestCase(APITestCase):
    def setUp(self):
        self.book = sample_book()
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@mail.com',
            password='PASSWORD',
        )
        self.client.force_authenticate(user=self.user)

    def test_authorized_book_retrieve(self):
        url = get_book_retrieve(self.book.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authorized_book_list(self):
        response = self.client.get(BOOKS_LIST_VIEW)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_book_method(self):
        data = {
            "title": "Test Book2",
            "author": "Test Author2",
            "cover": "Soft",
            "inventory": 102,
            "daily_fee": 102,
        }
        response = self.client.post(BOOKS_LIST_VIEW, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_book_method(self):
        data = {
            "title": "Test Book2",
            "author": "Test Author2",
            "cover": "Soft",
            "inventory": 102,
            "daily_fee": 102,
        }
        url = get_book_retrieve(self.book.pk)
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_book_method(self):
        url = get_book_retrieve(self.book.pk)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AuthorizedAminBookRetrieveAPITestCase(APITestCase):
    def setUp(self):
        self.book = sample_book()
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@mail.com',
            password='PASSWORD',
            is_staff=True,
        )
        self.client.force_authenticate(user=self.user)

    def test_post_book_method(self):
        data = {
            "title": "Test Book2",
            "author": "Test Author2",
            "cover": "H",
            "inventory": 102,
        }
        response = self.client.post(BOOKS_LIST_VIEW, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_put_book_method(self):
        data = {
            "title": "Test Book2",
            "author": "Test Author2",
            "cover": "H",
            "inventory": 102,
        }

        url = get_book_retrieve(self.book.pk)
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_book_method(self):
        url = get_book_retrieve(self.book.pk)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

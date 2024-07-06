from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from books_service.models import Book
from books_service.serializers import BookSerializer

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


class AuthorizedBookRetrieveAPITestCase(APITestCase):
    def setUp(self):
        self.book = sample_book()
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@mail.com',
            password='PASSWORD',
        )
        self.client.force_authenticate(user=self.user)

    def test_authorized_book_retrieve_serializer(self):
        serializer = BookSerializer(self.book)
        url = get_book_retrieve(self.book.pk)
        response = self.client.get(url)
        self.assertEqual(response.data, serializer.data)

    def test_authorized_book_list_serializer(self):
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        response = self.client.get(BOOKS_LIST_VIEW)
        self.assertEqual(response.data, serializer.data)

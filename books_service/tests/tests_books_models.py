from django.test import TestCase

from books_service.models import Book


class BooksModelsTestCase(TestCase):

    def test_books_str_method(self):
        new_book = Book(
            title="Test Book",
            author="Test Author",
            cover="Soft",
            inventory=10,
            daily_fee=10
        )
        self.assertEqual(str(new_book), new_book.title)

import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from books_service.models import Book
from borrowings_service.models import Borrowings, Payment


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


def sample_user(**params):
    default = {
        "email": "mail@mail.com",
        "password": "PASSWORD",
    }
    default.update(params)
    return get_user_model().objects.create(**default)


def sample_borrowing(**params):
    default = {
        "expected_return_date": timezone.now() + datetime.timedelta(days=1),
        "book": sample_book(**params),
        "user": sample_user(email="test@mail.com", password="PASSWORD"),
    }
    default.update(params)
    return Borrowings.objects.create(**default)


class TestBorrowingsModel(TestCase):
    def setUp(self):
        self.book = sample_book()
        self.user = sample_user()
        self.borrowings = Borrowings.objects.create(
            expected_return_date=timezone.now() + datetime.timedelta(days=1),
            book=self.book,
            user=self.user
        )

    def test_borrowings_str_method(self):
        self.assertEqual(str(self.borrowings),
                         f"{self.borrowings.pk} "
                         f"|Book: "
                         f"{self.borrowings.book.title},"
                         f" Borrowed at "
                         f"{str(self.borrowings.borrow_date)}"
                         f" - "
                         f"{self.borrowings.user.email}")


class TestPaymentsModel(TestCase):
    def setUp(self):
        self.book = sample_book()
        self.user = sample_user()
        self.borrowings = sample_borrowing()
        self.borrowings.book = self.book
        self.borrowings.user = self.user
        self.borrowings.save()
        self.payments = Payment.objects.create(
            status="Pending",
            type="Payment",
            borrowing_id=self.borrowings
        )

    def test_payments_str_method(self):
        self.assertEqual(str(self.payments),
                         f"payment: {self.payments.status}, "
                         f"{self.payments.type},"
                         f" {self.payments.borrowing_id}")

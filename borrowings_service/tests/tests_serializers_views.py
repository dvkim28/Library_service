import datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from books_service.models import Book
from borrowings_service.models import Borrowings, Payment

BORROWING_LIST = reverse("borrowings_service:borrowings-list")
PAYMENT_LIST = reverse("borrowings_service:payments-list")


def get_borrowing_details(borrowing_id):
    return reverse("borrowings_service:borrowings-detail", args=[borrowing_id])


def sample_book(**params):
    default = {
        "title": "Test Book",
        "author": "Test Author",
        "cover": "Soft",
        "inventory": 10,
        "daily_fee": 10.20
    }
    default.update(params)
    return Book.objects.create(**default)


def sample_borrowing(user=None, book=None, **params):
    if user is None:
        user = get_user_model().objects.create_user(
            email="admin@ad.com",
            password="<PASSWORD>",
        )
    if book is None:
        book = sample_book()
    default = {
        "expected_return_date": timezone.now() + datetime.timedelta(days=1),
        "book": book,
        "user": user,
    }
    default.update(params)
    return Borrowings.objects.create(**default)


def sample_payment(borrowing=None, **params):
    if borrowing is None:
        borrowing = sample_borrowing()
    default = {
        "status": "Pending",
        "type": "Payment",
        "borrowing_id": borrowing,
    }
    default.update(params)
    return Payment.objects.create(**default)


def get_payment_details(payment_id):
    return reverse("borrowings_service:payments-detail", args=[payment_id])


class TestUnAuthorizedViews(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=None)
        self.borrowing = sample_borrowing()

    def test_get_borrowing_details(self):
        url = get_borrowing_details(self.borrowing.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_borrowing_list(self):
        response = self.client.get(BORROWING_LIST)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_payment_details(self):
        url = get_payment_details(1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_payment_list(self):
        response = self.client.get(PAYMENT_LIST)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestAuthorizedViews(APITestCase):
    def setUp(self):
        self.test_user = get_user_model().objects.create_user(
            email="admiesfdsdfsdfsn@ad.com",
            password="<PASSWORD>",
            is_staff=False,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.test_user)
        self.borrowing = sample_borrowing(
            user=self.test_user,
        )

    def test_payments_money_to_pay_property(self):
        payment = Payment.objects.create(
            status="Pending",
            type="Payment",
            borrowing_id=self.borrowing,
        )
        self.borrowing.actual_return_date = (timezone.now() + datetime
                                             .timedelta(days=1))
        self.borrowing.save()
        expected_charge = payment.money_to_pay
        self.assertEqual(payment.money_to_pay, expected_charge)

    def test_payments_get_charge(self):
        payment = Payment.objects.create(
            status="Pending",
            type="Payment",
            borrowing_id=self.borrowing,
        )
        self.borrowing.actual_return_date = (timezone.now() + datetime
                                             .timedelta(days=20))
        self.borrowing.save()
        expected_charge = payment.get_charge()
        self.assertEqual(payment.get_charge(), expected_charge)

    def test_post_method_borrowings(self):
        book = sample_book(
            title="Test Booking.com",
        )
        data = {
            "expected_return_date": timezone.now().date(),
            "book": book.id,
            "user": self.test_user.id,
        }
        response = self.client.post(BORROWING_LIST, data)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete_method_borrowings(self):
        url = get_borrowing_details(self.borrowing.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

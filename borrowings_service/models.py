from django.contrib.auth import get_user_model
from django.db import models
from rest_framework.exceptions import ValidationError

from books_service.models import Book

PAYMENTS_CHOICE = [
    ("Pending", "Pending"),
    ("Paid", "Paid"),
]

PAYMENT_TYPE = [
    ("Payment", "PAYMENT"),
    ("Fine", "FINE"),
]


class Borrowings(models.Model):
    borrow_date = models.DateField()
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Borrowings"

    def __str__(self):
        return (
            f"{self.pk} "
            f"|Book: {self.book.title},"
            f" Borrowed at {str(self.borrow_date)} - {self.user.email}"
        )

    def validate_book(self):
        if self.book.inventory == 0:
            raise ValidationError("there are no books in the inventory!")

    def clean(self):
        super().clean()
        self.validate_book()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Payment(models.Model):
    status = models.CharField(
        choices=PAYMENTS_CHOICE,
        max_length=10,
        default="Pending")
    type = models.CharField(
        choices=PAYMENT_TYPE,
        max_length=10,
        default="Payment")
    borrowing_id = models.ForeignKey(Borrowings, on_delete=models.CASCADE)
    session_url = models.URLField(blank=True)
    session_id = models.TextField(blank=True)

    @property
    def money_to_pay(self):
        return self.get_charge()

    def __str__(self):
        return f"payment: {self.status}, {self.type}, {self.borrowing_id}"

    def get_charge(self):
        if self.borrowing_id.actual_return_date:
            borrow_date = self.borrowing_id.borrow_date
            return_date = self.borrowing_id.actual_return_date
            daily_fee = self.borrowing_id.book.daily_fee
            period = (return_date - borrow_date).days
            charge = daily_fee * period

            return charge
        return 0

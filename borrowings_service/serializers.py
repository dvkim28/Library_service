from rest_framework import serializers

from books_service.serializers import BookSerializer
from borrowings_service.models import Borrowings, Payment
from users_service.serializers import UserSerializer


class BorrowingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowings
        fields = "__all__"


class BorrowingListSerializer(BorrowingsSerializer):
    book = BookSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Borrowings
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        ]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "status",
            "type",
            "money_to_pay",
            "borrowing_id",
            "session_url",
            "session_id",
        ]

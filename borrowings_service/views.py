from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response

from books_service.models import Book
from borrowings_service.models import Borrowings, Payment
from borrowings_service.serializers import (
    PaymentSerializer,
    BorrowingListSerializer,
    BorrowingsSerializer,
)
from borrowings_service.tasks import send_telegram_message


class BorrowingsViewSet(viewsets.ModelViewSet):
    queryset = Borrowings.objects.all()
    serializer_class = BorrowingsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingsSerializer
        elif self.action == "list":
            return BorrowingListSerializer
        else:
            return BorrowingsSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        book_title = serializer.validated_data["book"]
        try:
            book = Book.objects.select_for_update().get(title=book_title)
        except Book.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        try:
            book.inventory -= 1
            book.save()
        except IntegrityError:
            return Response(
                {"error": "Book is out of stock"},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_create(serializer)
        send_telegram_message.delay(serializer.validated_data["user"].email)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        is_active = self.request.query_params.get("active")
        if is_active is not None:
            if is_active.lower() == "true":
                return self.queryset.filter(actual_return_date__isnull=False)
            elif is_active.lower() == "false":
                return self.queryset.filter(actual_return_date__isnull=True)
            else:
                return self.queryset.none()

        if self.request.user.is_staff:
            user_id = self.request.query_params.get("user_id")
            if user_id is not None:
                return self.queryset.filter(user_id=user_id)
            else:
                return self.queryset
        else:
            return self.queryset.filter(user=self.request.user)


class PaymentsViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


@api_view(["POST"])
def return_borrowings(request, pk):
    try:
        borrowing = Borrowings.objects.get(id=pk)
        if not borrowing.actual_return_date:
            with transaction.atomic():
                borrowing.actual_return_date = timezone.now()
                borrowing.book.inventory += 1
                borrowing.book.save()
                borrowing.save()
            serializer = BorrowingsSerializer(borrowing)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    except Borrowings.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

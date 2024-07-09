import stripe
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import IntegrityError, transaction
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiExample
)
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from books_service.models import Book
from borrowings_service.models import Borrowings, Payment
from borrowings_service.serializers import (
    BorrowingListSerializer,
    BorrowingsSerializer,
    PaymentSerializer,
)
from borrowings_service.tasks import (
    send_telegram_message,
    get_paid_for_borrowing
)
from config import settings
from config.settings import DOMAIN_URL

stripe.api_key = settings.STRIPE_SECRET_KEY


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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        book_title = serializer.validated_data["book"]

        try:
            book = Book.objects.get(title=book_title)
        except ObjectDoesNotExist:
            return Response({"error": "Book not found"},
                            status=status.HTTP_404_NOT_FOUND)
        except MultipleObjectsReturned:
            return Response(
                {"error": "Multiple books found with the same title"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if book.inventory <= 0:
            return Response(
                {"error": "Book is out of stock"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                book.inventory -= 1
                book.save()
        except IntegrityError:
            return Response(
                {"error": "Failed to update book inventory"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        borrowing = serializer.save()

        # Assuming borrowing_id is a ForeignKey to Borrowing model
        Payment.objects.create(borrowing_id=borrowing)
        create_stripe_payment(borrowing.id)
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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="is_active",
                description="Active borrowings its"
                            " borrowings where return day is None",
                required=False,
                type=str,
                examples=[
                    OpenApiExample(
                        "Example 1",
                        description='Find route with destination '
                                    '"Gare do Oriente"',
                        value='true'
                    )
                ],
            ),
            OpenApiParameter(
                name="user_id",
                description="Find borrowings by specific user. "
                            "Only for administrators",
                required=False,
                type=str,
                examples=[
                    OpenApiExample(
                        "Example 1",
                        description='Find borrowings by specific user',
                        value='1'
                    )
                ],
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class PaymentsViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return self.queryset.filter(borrowing_id__user=self.request.user)


def create_stripe_payment(borrowing_id):
    borrowing = Borrowings.objects.get(id=borrowing_id)
    payment = Payment.objects.get(borrowing_id=borrowing)
    amount_to_pay = get_fee_if_borrowing_overdue(borrowing)
    price = stripe.Price.create(
        unit_amount=int(amount_to_pay * 100),
        currency="usd",
        product_data={"name": f"Payment for borrowing {borrowing.book.title}"},
    )
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price": price.id,
                    "quantity": 1,
                },
            ],
            mode="payment",
            success_url=DOMAIN_URL + "/success.html",
            cancel_url=DOMAIN_URL + "/cancel.html",
            metadata={
                "payment_pk": payment.id,
            },
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    payment.session_url = checkout_session.url
    payment.session_id = checkout_session.id
    payment.save()
    return Response(checkout_session, status=status.HTTP_201_CREATED)


def get_fee_if_borrowing_overdue(borrowing):
    expected_return_date = borrowing.expected_return_date
    borrow_date = borrowing.borrow_date
    daily_fee = borrowing.book.daily_fee

    if timezone.now().date() > expected_return_date:
        overdue_days = (timezone.now().date() - expected_return_date).days
        amount_to_pay = ((borrowing.expected_period * daily_fee)
                         + (overdue_days * 2))
    else:
        real_period = (timezone.now().date() - borrow_date).days
        amount_to_pay = real_period * daily_fee

    return amount_to_pay


@csrf_exempt
def webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = (stripe.Webhook
                 .construct_event(payload, sig_header, endpoint_secret))
    except ValueError as e:
        # Invalid payload
        print(f"Invalid payload: {e}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print(f"Invalid signature: {e}")
        return HttpResponse(status=400)
    except Exception as e:
        # Catch any other unexpected exceptions
        print(f"Unexpected error: {e}")
        return HttpResponse(status=500)

    # Handle the event
    if event["type"] == "checkout.session.completed":
        try:
            payment_pk = event["data"]["object"]["metadata"]["payment_pk"]
            print(payment_pk)
            get_paid_for_borrowing.delay(payment_pk)
        except Exception:
            return HttpResponse(status=500)
    return HttpResponse(status=200)

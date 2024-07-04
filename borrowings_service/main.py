import os
import django
from django.utils import timezone
from borrowings_service.models import Borrowings

from borrowings_service.tasks import send_telegram_borrowed_task

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()


def get_expired_borrowers():
    borrowers_list = []
    borrowings = Borrowings.objects.filter(actual_return_date__isnull=True)
    current_datetime = timezone.now().date()
    for borrowing in borrowings:
        if borrowing.expected_return_date is not None:
            expiration_days = (
                (current_datetime - borrowing.expected_return_date)
                .days)
            borrower_data = {
                "borrower": borrowing.user.email,
                "expiration": expiration_days
            }
            borrowers_list.append(borrower_data)
    send_telegram_borrowed_task(borrowers_list)


if __name__ == "__main__":
    get_expired_borrowers()

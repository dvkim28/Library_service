import os

import django
import requests
from celery import Celery, shared_task
from celery.beat import logger
from django.utils import timezone

from borrowings_service.models import Borrowings, Payment
from config.settings import CHAT_ID, TOKEN

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

app = Celery("telegram_bot", broker="redis://localhost")


@shared_task
def send_telegram_message(borrow_user: str):
    if borrow_user:
        message = f"There is a new borrowing from {borrow_user}"
        url = (
            f"https://api.telegram.org/bot{TOKEN}"
            f"/sendMessage?chat_id={CHAT_ID}&text={message}"
        )
        requests.get(url)


@shared_task
def get_paid_for_borrowing(payment_pk: int) -> None:
    payment = Payment.objects.get(id=payment_pk)
    payment.status = "Paid"
    payment.borrowing_id.actual_return_date = timezone.now().date()
    payment.borrowing_id.book.inventory += 1
    payment.borrowing_id.book.save()
    payment.borrowing_id.save()
    payment.save()


@shared_task
def get_expired_borrowers_daily():
    borrowers_list = []
    borrowings = Borrowings.objects.filter(actual_return_date__isnull=True)
    current_datetime = timezone.now().date()
    if len(borrowings) > 0:
        for borrowing in borrowings:
            if borrowing.expected_return_date is not None:
                expiration_days = (
                    current_datetime - borrowing.expected_return_date
                ).days
                borrower_data = {
                    "borrower": borrowing.user.email,
                    "expiration": expiration_days,
                }
                borrowers_list.append(borrower_data)
    send_telegram_borrowed_task(borrowers_list)


def send_telegram_borrowed_task(borrowers_list: list):
    if len(borrowers_list) > 0:
        message = "There are/is borrowers\n"
        counter = 1
        for borrower in borrowers_list:
            user_email = borrower["borrower"]
            expiration = borrower["expiration"]
            message += f"{counter}. {user_email}" \
                       f" - overdue for {expiration} day/s\n"
            counter += 1
    else:
        message = "No borrowings overdue today!"
    try:
        url = (
            f"https://api.telegram.org/bot{TOKEN}"
            f"/sendMessage?chat_id={CHAT_ID}&text={message}"
        )
        response = requests.get(url)
        response.raise_for_status()
        logger.info(
            f"Telegram message sent successfully with status code "
            f"{response.status_code}"
        )
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send Telegram message: {e}")

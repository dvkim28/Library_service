import os
import django
from celery.beat import logger
from django.utils import timezone
import requests
from celery import Celery, shared_task

from config.settings import CHAT_ID, TOKEN
from borrowings_service.models import Borrowings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()


app = Celery('telegram_bot', broker='redis://localhost')


@shared_task
def send_telegram_message(borrow_user: str):
    if borrow_user:
        message = (f"There is a new borrowing from {borrow_user}")
        url = (f"https://api.telegram.org/bot{TOKEN}"
               f"/sendMessage?chat_id={CHAT_ID}&text={message}")
        requests.get(url)


@shared_task
def get_expired_borrowers():
    borrowers_list = []
    borrowings = Borrowings.objects.filter(actual_return_date__isnull=True)
    current_datetime = timezone.now().date()
    for borrowing in borrowings:
        if borrowing.expected_return_date is not None:
            expiration_days = (
                (current_datetime - borrowing.expected_return_date).days)
            borrower_data = {
                "borrower": borrowing.user.email,
                "expiration": expiration_days
            }
            borrowers_list.append(borrower_data)
    send_telegram_borrowed_task(borrowers_list)


def send_telegram_borrowed_task(borrowers_list: list):
    if not borrowers_list:
        return

    message = "There are/is borrowers\n"
    counter = 1
    for borrower in borrowers_list:
        user_email = borrower["borrower"]
        expiration = borrower["expiration"]
        message += (f"{counter}. {user_email}"
                    f" - borrowed for {expiration} day/s\n")
        counter += 1
    url = (f"https://api.telegram.org/bot{TOKEN}"
           f"/sendMessage?chat_id={CHAT_ID}&text={message}")

    try:
        response = requests.get(url)
        response.raise_for_status()
        logger.info(f"Telegram message sent successfully with status code "
                    f"{response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send Telegram message: {e}")

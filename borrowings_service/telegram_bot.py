import os

import django
import requests
from borrowings_service.models import Borrowings

TOKEN = "7248679095:AAG9liBAlkcXY6coIDnpToaZnzO940afRWs"
CHAT_ID = 826544103
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()


def send_telegram_message(borrowings_id):
    if borrowings_id:
        try:
            borrowings = Borrowings.objects.get(id=borrowings_id)
            message = (
                f"There is a new borrowing from {borrowings.user.email}, "
                f"book: {borrowings.book}, "
                f"expected return date: {borrowings.expected_return_date}"
            )
            url = (
                f"https://api.telegram.org/bot{TOKEN}"
                f"/sendMessage?chat_id={CHAT_ID}&text={message}"
            )
            response = requests.get(url)
            return response.json()
        except Borrowings.DoesNotExist:
            return {"error": "Borrowings does not exist"}
    return {"error": "Invalid borrowings_id"}


result = send_telegram_message(1)
print(result)

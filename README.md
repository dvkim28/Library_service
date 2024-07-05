# library_service

 celery -A config  worker --loglevel=info
 celery -A config beat -l info
stripe listen --forward-to http://localhost:8000/api/v1/borrowings_service/webhook/stripe/
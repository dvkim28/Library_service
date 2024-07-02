from django.contrib import admin

from borrowings_service.models import Borrowings, Payment

admin.site.register(Borrowings)
admin.site.register(Payment)

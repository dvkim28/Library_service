from django.urls import include, path
from rest_framework import routers

from borrowings_service.views import (
    BorrowingsViewSet,
    PaymentsViewSet,
    webhook,
)

router = routers.DefaultRouter()
router.register("borrowings", BorrowingsViewSet)
router.register("payments", PaymentsViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("webhook/stripe", webhook, name="webhook"),
]

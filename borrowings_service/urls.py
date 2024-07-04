from django.urls import include, path
from rest_framework import routers

from borrowings_service.views import (
    BorrowingsViewSet,
    PaymentsViewSet,
    post,
    return_borrowings,
    webhook,
)

router = routers.DefaultRouter()
router.register("borrowings", BorrowingsViewSet)
router.register("payments", PaymentsViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("borrowings/<int:pk>/return/", return_borrowings, name="return_borrowings"),
    path("<int:pk>/create-checkout-session/", post, name="create-checkout-session"),
    path("webhook/stripe", webhook, name="webhook"),
]

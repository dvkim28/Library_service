from django.urls import path, include
from rest_framework import routers

from borrowings_service.views import (
    BorrowingsViewSet,
    PaymentsViewSet,
    return_borrowings,
)

router = routers.DefaultRouter()
router.register("borrowings", BorrowingsViewSet)
router.register("payments", PaymentsViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("borrowings/<int:pk>/return/",
         return_borrowings, name="return_borrowings"),
]

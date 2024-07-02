from django.urls import path, include
from rest_framework import routers

from books_service.views import BookListView

router = routers.DefaultRouter()
router.register("books", BookListView)

urlpatterns = [
    path("", include(router.urls)),
]

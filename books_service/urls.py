from django.urls import include, path
from rest_framework import routers

from books_service.views import BookListView

router = routers.DefaultRouter()
router.register("books", BookListView)

urlpatterns = [
    path("", include(router.urls)),
]

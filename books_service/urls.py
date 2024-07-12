from django.urls import include, path
from rest_framework import routers

from books_service.views import BookModelView

router = routers.DefaultRouter()
router.register("books", BookModelView)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "books_service"

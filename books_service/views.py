from rest_framework import viewsets

from books_service.models import Book
from books_service.serializers import BookSerializer
from borrowings_service.permissions import AdminAllRestRead


class BookListView(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (AdminAllRestRead,)

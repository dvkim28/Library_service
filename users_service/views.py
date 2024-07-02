from django.contrib.auth import get_user_model
from rest_framework import viewsets, generics

from users_service.models import User
from users_service.serializers import UserSerializer, ManageUserSerializer


class UserModelView(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = ManageUserSerializer
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user

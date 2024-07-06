from django.contrib.auth import get_user_model
from rest_framework import generics, viewsets, permissions

from users_service.serializers import ManageUserSerializer, UserSerializer


class UserModelView(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = ManageUserSerializer
    queryset = get_user_model().objects.all()

    def get_object(self):
        return self.request.user


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)

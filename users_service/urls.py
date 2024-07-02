from django.urls import path, include
from rest_framework import routers

from users_service.views import UserModelView, ManageUserView

router = routers.DefaultRouter()
router.register("users", UserModelView)

urlpatterns = [
    path("", include(router.urls)),
    path("me/", ManageUserView.as_view(), name="manage-user"),
]

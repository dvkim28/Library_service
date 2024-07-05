from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from users_service.views import ManageUserView, UserModelView

router = routers.DefaultRouter()
router.register("users", UserModelView)

urlpatterns = [
    path("", include(router.urls)),
    path("me/", ManageUserView.as_view(), name="manage-user"),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify/', TokenVerifyView.as_view(), name='token_verify'),

]

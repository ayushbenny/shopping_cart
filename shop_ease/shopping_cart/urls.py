from django.urls import path

from shopping_cart.utils import CustomRefreshTokenObtainPairView, CustomTokenObtainPairView
from shopping_cart.views import FetchUserAPIView, RegisterUserAPIView


urlpatterns = [
    path("api/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path(
        "api/token/refresh/",
        CustomRefreshTokenObtainPairView.as_view(),
        name="token_refresh",
    ),
    path("user/", RegisterUserAPIView.as_view(), name="register_user"),
    path("fetch_user/", FetchUserAPIView.as_view(), name="fetch_user"),
]

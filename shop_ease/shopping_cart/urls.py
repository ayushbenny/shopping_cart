from django.urls import path

from shopping_cart.utils import (
    CustomRefreshTokenObtainPairView,
    CustomTokenObtainPairView,
)
from shopping_cart.views import (
    ManageOrderAPIView,
    ManageProductAPIView,
    ManagePurchaseAPIView,
    ManageUserAPIView,
    RegisterUserAPIView,
)


urlpatterns = [
    path("api/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path(
        "api/token/refresh/",
        CustomRefreshTokenObtainPairView.as_view(),
        name="token_refresh",
    ),
    path("user/", RegisterUserAPIView.as_view(), name="register_user"),
    path("api/user/", ManageUserAPIView.as_view(), name="fetch_user"),
    path("api/product/", ManageProductAPIView.as_view(), name="manage_product"),
    path("api/order/", ManageOrderAPIView.as_view(), name="manage_order"),
    path("api/payment/", ManagePurchaseAPIView.as_view(), name="manage_payment"),
]

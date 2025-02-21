from django.urls import path
from .views import (
    RegisterView,
    LogoutView,
    UserDetailView,
    ProfileUpdateView,
    ChangePasswordView,
    CustomPasswordResetView,
    CustomPasswordResetConfirmView,
    CustomTokenObtainPairView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", UserDetailView.as_view(), name="user-detail"),
    path("me/update/", ProfileUpdateView.as_view(), name="profile-update"),
    path("me/change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("reset-password/", CustomPasswordResetView.as_view(), name="reset-password"),
    path(
        "reset-password/confirm/",
        CustomPasswordResetConfirmView.as_view(),
        name="reset-password-confirm",
    ),
]

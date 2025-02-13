from django.urls import path
from .views import (
    RegisterView,
    LogoutView,
    UserDetailView,
    ProfileUpdateView,
    ChangePasswordView,
    CheckAdminStatusView,
)
from rest_framework.authtoken import views as auth_views

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", auth_views.obtain_auth_token, name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", UserDetailView.as_view(), name="user-detail"),
    path("me/update/", ProfileUpdateView.as_view(), name="profile-update"),
    path("me/change-password/", ChangePasswordView.as_view(), name="change-password"),
    path(
        "check-admin-status/", CheckAdminStatusView.as_view(), name="check_admin_status"
    ),
]

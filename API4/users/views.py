from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    ProfileSerializer,
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
)
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from .tasks import send_reset_email, send_registration_notification
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from urllib.parse import urlparse, parse_qs
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .logs_service import log_to_kafka
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import serializers


User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        log_to_kafka(
            message="Registration attempt.", level="info", extra_data=request.data
        )
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            refresh = RefreshToken.for_user(user)
            refresh["username"] = user.username
            refresh["is_admin"] = user.is_superuser or user.is_staff

            access_token = refresh.access_token
            access_token["username"] = user.username
            access_token["is_admin"] = user.is_superuser or user.is_staff

            log_to_kafka(
                message="User registered successfully.",
                level="info",
                extra_data={
                    "user_id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
            )
            send_registration_notification.delay(user.email)
            return Response(
                {
                    "message": "User registered successfully.",
                    "user": UserSerializer(user).data,
                    "access": str(access_token),
                    "refresh": str(refresh),
                },
                status=status.HTTP_201_CREATED,
            )
        except serializers.ValidationError as e:
            error_details = e.detail
            log_to_kafka(
                message="User registration failed.",
                level="error",
                extra_data={"error": str(e)},
            )
            return Response(
                {"errors": error_details},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            log_to_kafka(
                message="User registration failed.",
                level="error",
                extra_data={"error": str(e)},
            )
            return Response(
                {"error": "Registration failed."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"error": "Refresh token required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            log_to_kafka(
                message="User logged out successfully.",
                level="info",
                extra_data={"user_id": request.user.id},
            )
            return Response(
                {"message": "Logged out successfully."}, status=status.HTTP_200_OK
            )
        except Token.DoesNotExist:
            log_to_kafka(
                message="Token not found during logout.",
                level="warning",
                extra_data={"user_id": request.user.id},
            )
            return Response(
                {"error": "Token not found."}, status=status.HTTP_400_BAD_REQUEST
            )


class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        log_to_kafka(
            message="User detail retrieval.",
            level="info",
            extra_data={"user_id": request.user.id},
        )
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class ProfileUpdateView(generics.UpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        log_to_kafka(
            message="Profile update attempt.",
            level="info",
            extra_data={"user_id": request.user.id, "data": request.data},
        )
        response = super().update(request, *args, **kwargs)

        log_to_kafka(
            message="Profile updated successfully.",
            level="info",
            extra_data={"user_id": request.user.id},
        )
        return response


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]


class CustomPasswordResetView(APIView):
    def post(self, request, *args, **kwargs):
        log_to_kafka(
            message="Password reset request initiated.",
            level="info",
            extra_data={"email": request.data.get("email")},
        )

        email = request.data.get("email")
        if not email:
            return Response(
                {"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        User = get_user_model()
        user = None
        try:
            user = User.objects.get(email=email)
            log_to_kafka(
                message="User found for password reset.",
                level="info",
                extra_data={"user_id": user.id, "email": email},
            )
        except ObjectDoesNotExist:
            log_to_kafka(
                message="Password reset requested for non-existent email.",
                level="warning",
                extra_data={"email": email},
            )

        if user:
            protocol = "https" if self.request.is_secure() else "http"
            domain = self.request.get_host()
            if not domain:
                return Response(
                    {"error": "Domain is required."}, status=status.HTTP_400_BAD_REQUEST
                )

            send_reset_email.delay(user.id, domain, protocol)
            log_to_kafka(
                message="Password reset email sent (task dispatched).",
                level="info",
                extra_data={"user_id": user.id, "email": email},
            )

        return Response(
            {
                "detail": "If an account with that email exists, a password reset email has been sent."
            },
            status=status.HTTP_200_OK,
        )


class CustomPasswordResetView(APIView):
    def post(self, request, *args, **kwargs):
        log_to_kafka(
            message="Password reset request initiated.",
            level="info",
            extra_data={"email": request.data.get("email")},
        )

        email = request.data.get("email")
        if not email:
            return Response(
                {"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        User = get_user_model()
        try:
            user = User.objects.get(email=email)
            log_to_kafka(
                message="User found for password reset.",
                level="info",
                extra_data={"user_id": user.id, "email": email},
            )
        except ObjectDoesNotExist:
            log_to_kafka(
                message="Password reset requested for non-existent email.",
                level="warning",
                extra_data={"email": email},
            )
            pass

        protocol = "https" if self.request.is_secure() else "http"
        domain = self.request.get_host()
        if not domain:
            return Response(
                {"error": "Domain is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        send_reset_email.delay(user.id, domain, protocol)
        log_to_kafka(
            message="Password reset email sent (task dispatched).",
            level="info",
            extra_data={"user_id": user.id, "email": email},
        )

        return Response(
            {
                "detail": "If an account with that email exists, a password reset email has been sent."
            },
            status=status.HTTP_200_OK,
        )


class CustomPasswordResetConfirmView(APIView):
    def post(self, request, *args, **kwargs):
        log_to_kafka(
            message="Password reset confirmation initiated.",
            level="info",
            extra_data={"url": request.build_absolute_uri()},
        )
        url = request.build_absolute_uri()
        query_params = parse_qs(urlparse(url).query)
        uidb64 = query_params.get("uidb64", [None])[0]
        token = query_params.get("token", [None])[0]

        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        if not uidb64 or not token or not new_password or not confirm_password:
            log_to_kafka(
                message="Password reset confirmation failed - Missing parameters.",
                level="warning",
                extra_data={
                    "uidb64": uidb64,
                    "token": token,
                    "new_password": bool(new_password),
                    "confirm_password": bool(confirm_password),
                },
            )
            return Response(
                {
                    "detail": "UID, token, new password, and confirm password are required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if new_password != confirm_password:
            log_to_kafka(
                message="Password reset failed - Passwords do not match.",
                level="warning",
                extra_data={"uidb64": uidb64},
            )
            return Response(
                {"detail": "Passwords do not match."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_user_model().objects.get(pk=uid)
            log_to_kafka(
                message="User found for password reset confirmation.",
                level="info",
                extra_data={"user_id": user.id},
            )
        except (TypeError, ValueError, OverflowError, ObjectDoesNotExist):
            log_to_kafka(
                message="Password reset failed - Invalid link or user not found.",
                level="error",
                extra_data={"uidb64": uidb64},
            )
            return Response(
                {"detail": "Invalid link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if default_token_generator.check_token(user, token):
            try:
                validate_password(new_password, user)
            except ValidationError as e:
                log_to_kafka(
                    message="Password reset failed - Password validation error.",
                    level="error",
                    extra_data={"user_id": user.id, "error": str(e)},
                )
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()
            log_to_kafka(
                message="Password reset successful.",
                level="info",
                extra_data={"user_id": user.id},
            )
            return Response(
                {"detail": "Password has been reset."},
                status=status.HTTP_200_OK,
            )
        else:
            log_to_kafka(
                message="Password reset failed - Invalid or expired token.",
                level="warning",
                extra_data={"user_id": user.id, "token": token},
            )
            return Response(
                {"detail": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

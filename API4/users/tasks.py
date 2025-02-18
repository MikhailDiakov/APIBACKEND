# tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from .logs_service import log_to_kafka


def generate_reset_password_url(user, domain, protocol):
    try:
        uidb64 = urlsafe_base64_encode(str(user.pk).encode("utf-8"))
        token = default_token_generator.make_token(user)

        reset_url = f"{protocol}://{domain}/api/v1/users/reset-password/confirm/?uidb64={uidb64}&token={token}"
        log_to_kafka(
            message="Password reset URL generated successfully.",
            level="info",
            extra_data={"user_id": user.id, "reset_url": reset_url},
        )
        return reset_url
    except Exception as e:
        log_to_kafka(
            message="Error generating password reset URL.",
            level="error",
            extra_data={"user_id": user.id, "error": str(e)},
        )
        raise


@shared_task
def send_reset_email(user_id, domain, protocol):
    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
        log_to_kafka(
            message="User found for password reset email.",
            level="info",
            extra_data={"user_id": user.id, "email": user.email},
        )
        reset_url = generate_reset_password_url(user, domain, protocol)
        send_mail(
            "Password Reset",
            f"Click the link to reset your password: {reset_url}",
            "no-reply@example.com",
            [user.email],
            fail_silently=False,
        )
        log_to_kafka(
            message="Password reset email sent successfully.",
            level="info",
            extra_data={"user_id": user.id, "email": user.email},
        )
    except User.DoesNotExist:
        log_to_kafka(
            message="User not found for password reset email.",
            level="warning",
            extra_data={"user_id": user_id},
        )
    except Exception as e:
        log_to_kafka(
            message="Error sending password reset email.",
            level="error",
            extra_data={"user_id": user_id, "error": str(e)},
        )

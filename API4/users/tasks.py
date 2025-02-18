from celery import shared_task
from .notifications_service import send_notification_to_kafka
from django.contrib.auth import get_user_model
from .logs_service import log_to_kafka
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode


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
def send_reset_email(id, domain, protocol):
    try:
        User = get_user_model()
        user = User.objects.get(id=id)
        email = user.email
        reset_url = generate_reset_password_url(user, domain, protocol)
        send_notification_to_kafka(
            event_type="password_reset_requested",
            reset_url=reset_url,
            email=email,
        )
    except User.DoesNotExist:
        log_to_kafka(
            message="User not found for password reset email.",
            level="warning",
            extra_data={"user_id": id},
        )
    except Exception as e:
        log_to_kafka(
            message="Error sending password reset email.",
            level="error",
            extra_data={"user_id": id, "error": str(e)},
        )

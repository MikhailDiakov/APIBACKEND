from celery import shared_task
from django.core.mail import send_mail
from .logs_service import log_to_kafka


@shared_task
def send_reset_email_notifications(reset_url, email):
    try:
        reset_url = reset_url
        send_mail(
            "Password Reset",
            f"Click the link to reset your password: {reset_url}",
            "no-reply@example.com",
            [email],
            fail_silently=False,
        )
        log_to_kafka(
            message="Password reset email sent successfully.",
            level="info",
            extra_data={"email": email},
        )
    except Exception as e:
        log_to_kafka(
            message="Error sending password reset email.",
            level="error",
            extra_data={"email": email, "error": str(e)},
        )

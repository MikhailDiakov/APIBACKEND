from celery import shared_task
from django.core.mail import send_mail
from .logs_service import log_to_kafka


@shared_task
def send_reset_email_notifications(reset_url, email):
    try:
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


@shared_task
def send_registration_email_notifications(email):
    try:
        send_mail(
            "Welcome!",
            "Thank you for registering on our platform.",
            "no-reply@example.com",
            [email],
            fail_silently=False,
        )
        log_to_kafka(
            message="Registration email sent successfully.",
            level="info",
            extra_data={"email": email},
        )
    except Exception as e:
        log_to_kafka(
            message="Error sending registration email.",
            level="error",
            extra_data={"email": email, "error": str(e)},
        )


@shared_task
def send_order_paid_email_notifications(email, order_id):
    try:
        send_mail(
            "Order Payment Confirmation",
            f"Your order {order_id} has been successfully paid. Expect a call soon!",
            "no-reply@example.com",
            [email],
            fail_silently=False,
        )
        log_to_kafka(
            message="Order payment confirmation email sent successfully.",
            level="info",
            extra_data={"email": email, "order_id": order_id},
        )
    except Exception as e:
        log_to_kafka(
            message="Error sending order payment confirmation email.",
            level="error",
            extra_data={"email": email, "order_id": order_id, "error": str(e)},
        )

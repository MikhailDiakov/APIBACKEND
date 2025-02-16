# tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode


def generate_reset_password_url(user, domain, protocol):
    uidb64 = urlsafe_base64_encode(str(user.pk).encode("utf-8"))
    token = default_token_generator.make_token(user)

    reset_url = f"{protocol}://{domain}/api/v1/users/reset-password/confirm/?uidb64={uidb64}&token={token}"
    return reset_url


@shared_task
def send_reset_email(user_id, domain, protocol):
    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
        reset_url = generate_reset_password_url(user, domain, protocol)
        send_mail(
            "Password Reset",
            f"Click the link to reset your password: {reset_url}",
            "no-reply@example.com",
            [user.email],
            fail_silently=False,
        )
    except User.DoesNotExist:
        pass

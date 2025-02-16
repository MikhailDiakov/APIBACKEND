from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from .models import Order


@shared_task(bind=True, max_retries=3)
def update_order_task(
    self, order_id, status_value=None, is_paid=None, payment_intent=None
):
    try:
        with transaction.atomic():
            order = Order.objects.get(id=order_id)

            if status_value:
                if status_value not in [
                    Order.PENDING,
                    Order.COMPLETED,
                    Order.CANCELLED,
                ]:
                    raise ValueError("Invalid status value.")
                order.status = status_value

            if is_paid is not None:
                order.is_paid = is_paid

            if payment_intent:
                order.payment_intent = payment_intent

            order.save()

    except ObjectDoesNotExist:
        raise self.retry(
            countdown=5, max_retries=3, exc=ObjectDoesNotExist("Order not found.")
        )
    except Exception as e:
        raise self.retry(countdown=5, max_retries=3, exc=e)

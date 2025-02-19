from django.core.management.base import BaseCommand
import time
import json
from kafka import KafkaConsumer
import os
from notifications.tasks import (
    send_reset_email_notifications,
    send_order_paid_email_notifications,
    send_registration_email_notifications,
)
from notifications.logs_service import log_to_kafka


class Command(BaseCommand):
    help = "Run Kafka consumer"

    def handle(self, *args, **kwargs):
        def create_consumer():
            consumer = None
            while not consumer:
                try:
                    consumer = KafkaConsumer(
                        "notifications",
                        bootstrap_servers=os.environ["KAFKA_BROKER"],
                    )
                except Exception as e:
                    log_to_kafka(
                        message="Failed to create Kafka consumer",
                        level="error",
                        extra_data={"error": str(e)},
                    )
                    time.sleep(5)
            return consumer

        consumer = create_consumer()

        for message in consumer:
            print(f"Received message: {message.value.decode()}")
            try:
                data_message = message.value.decode()
                data = json.loads(data_message)
                event_type = data.get("event_type")
                email = data.get("email")
                reset_url = data.get("reset_url")
                order_id = data.get("order_id")

                if event_type == "password_reset_requested":
                    if not email:
                        raise ValueError(
                            "Missing email for password reset notification"
                        )
                    send_reset_email_notifications.delay(reset_url, email)
                    log_to_kafka(
                        message="send_reset_email task created",
                        level="info",
                        extra_data={"email": email, "event_type": event_type},
                    )
                elif event_type == "user_registered":
                    if not email:
                        raise ValueError("Missing email for registration notification")
                    send_registration_email_notifications.delay(email)
                    log_to_kafka(
                        message="send_registration_email task created",
                        level="info",
                        extra_data={"email": email, "event_type": event_type},
                    )
                elif event_type == "order_paid":
                    if not email or not order_id:
                        raise ValueError(
                            "Missing email or order_id for order paid notification"
                        )
                    send_order_paid_email_notifications.delay(email, order_id)
                    log_to_kafka(
                        message="send_order_paid_email task created",
                        level="info",
                        extra_data={
                            "email": email,
                            "event_type": event_type,
                            "order_id": order_id,
                        },
                    )
                else:
                    log_to_kafka(
                        message="Unknown event type",
                        level="warning",
                        extra_data={"event_type": event_type},
                    )
            except Exception as e:
                log_to_kafka(
                    message="Failed to process Kafka message",
                    level="error",
                    extra_data={"error": str(e), "message": message.value},
                )

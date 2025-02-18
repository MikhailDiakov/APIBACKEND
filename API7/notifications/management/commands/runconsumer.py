from django.core.management.base import BaseCommand
import time
import json
from kafka import KafkaConsumer
import os
from notifications.tasks import send_reset_email_notifications
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
                print(f"Parsed message: {data}")
                event_type = data.get("event_type")
                reset_url = data.get("reset_url")
                email = data.get("email")

                if event_type == "password_reset_requested":
                    print("PASSWORD RESET REQUESTED")
                    send_reset_email_notifications.delay(reset_url, email)
                    log_to_kafka(
                        message="send_reset_email task created",
                        level="info",
                        extra_data={"email": email, "event_type": event_type},
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

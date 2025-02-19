from kafka import KafkaProducer
import json
import logging


def send_notification_to_kafka(event_type, reset_url, email):
    try:
        producer = KafkaProducer(
            bootstrap_servers="kafka:9092",
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

        notification_data = {
            "event_type": event_type,
            "reset_url": reset_url,
            "email": email,
        }

        producer.send("notifications", notification_data)
        producer.flush()
        logging.info(f"Notification for event {event_type} sent to Kafka.")
    except Exception as e:
        logging.error(f"Failed to send notification to Kafka: {str(e)}")

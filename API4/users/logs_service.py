from kafka import KafkaProducer
import json
import logging


def log_to_kafka(message, level="info", extra_data=None):
    try:
        producer = KafkaProducer(
            bootstrap_servers="kafka:9092",
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

        log_data = {
            "level": level,
            "message": message,
            "extra_data": extra_data,
        }

        producer.send("logs", log_data)
        producer.flush()
    except Exception as e:
        logging.error(f"Failed to log to Kafka: {str(e)}")

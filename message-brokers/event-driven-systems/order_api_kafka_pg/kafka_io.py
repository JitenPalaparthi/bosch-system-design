
import os, json
from kafka import KafkaProducer, KafkaConsumer

BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
ORDERS_TOPIC = os.getenv("ORDERS_TOPIC", "orders_created")

def make_producer():
    return KafkaProducer(
        bootstrap_servers=BOOTSTRAP,
        acks="all",
        linger_ms=5,
        retries=3,
        value_serializer=lambda d: json.dumps(d).encode("utf-8"),
        key_serializer=lambda k: (k.encode("utf-8") if isinstance(k, str) else k),
    )

def make_consumer(group_id="orders_consumer_group"):
    return KafkaConsumer(
        ORDERS_TOPIC,
        bootstrap_servers=BOOTSTRAP,
        group_id=group_id,
        enable_auto_commit=True,
        auto_offset_reset="earliest",
        value_deserializer=lambda b: json.loads(b.decode("utf-8")),
    )

import json
import os
import time
from decimal import Decimal

from kafka import KafkaConsumer
from opensearchpy import OpenSearch

SERVICE_NAME = os.getenv("SERVICE_NAME", "projector-service")
BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
TOPIC = os.getenv("KAFKA_TOPIC", "cdc.public.orders")
INDEX_NAME = os.getenv("OPENSEARCH_INDEX", "orders_read")
OPENSEARCH_URL = os.getenv("OPENSEARCH_URL", "http://opensearch:9200")

client = OpenSearch(
    hosts=[OPENSEARCH_URL],
    http_compress=True,
    use_ssl=False,
    verify_certs=False,
)

INDEX_MAPPING = {
    "settings": {"number_of_shards": 1, "number_of_replicas": 0},
    "mappings": {
        "properties": {
            "order_id": {"type": "keyword"},
            "customer_id": {"type": "keyword"},
            "customer_name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "item": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "quantity": {"type": "integer"},
            "price": {"type": "double"},
            "status": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "tracking_id": {"type": "keyword"},
            "search_text": {"type": "text"},
            "created_at": {"type": "date"},
            "updated_at": {"type": "date"},
        }
    },
}


def wait_for_opensearch():
    for attempt in range(1, 61):
        try:
            if client.ping():
                if not client.indices.exists(index=INDEX_NAME):
                    client.indices.create(index=INDEX_NAME, body=INDEX_MAPPING)
                    print(f"[{SERVICE_NAME}] Created index {INDEX_NAME}")
                return
        except Exception as exc:
            print(f"[{SERVICE_NAME}] OpenSearch not ready ({attempt}/60): {exc}")
        time.sleep(3)
    raise RuntimeError("OpenSearch is not available")


def decimal_to_float(value):
    if isinstance(value, Decimal):
        return float(value)
    return value


def normalize_record(record: dict) -> dict:
    return {
        "order_id": record["order_id"],
        "customer_id": record["customer_id"],
        "customer_name": record["customer_name"],
        "item": record["item"],
        "quantity": int(record["quantity"]),
        "price": float(record["price"]),
        "status": record["status"],
        "tracking_id": record.get("tracking_id"),
        "created_at": record["created_at"],
        "updated_at": record["updated_at"],
        "search_text": " ".join(
            [
                str(record.get("customer_name", "")),
                str(record.get("item", "")),
                str(record.get("status", "")),
                str(record.get("customer_id", "")),
            ]
        ).strip(),
    }


def apply_event(event: dict):
    payload = event.get("payload", event)
    op = payload.get("op")
    after = payload.get("after")
    before = payload.get("before")

    if op in ("c", "r", "u") and after:
        doc = normalize_record(after)
        client.index(index=INDEX_NAME, id=doc["order_id"], body=doc, refresh=True)
        print(f"[{SERVICE_NAME}] Upserted order {doc['order_id']} from op={op}")
    elif op == "d" and before:
        order_id = before["order_id"]
        client.delete(index=INDEX_NAME, id=order_id, ignore=[404], refresh=True)
        print(f"[{SERVICE_NAME}] Deleted order {order_id}")


def wait_for_kafka_consumer():
    last_error = None
    for attempt in range(1, 61):
        try:
            consumer = KafkaConsumer(
                TOPIC,
                bootstrap_servers=BOOTSTRAP,
                group_id="orders-projector-group",
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            )
            print(f"[{SERVICE_NAME}] Connected to Kafka topic {TOPIC}")
            return consumer
        except Exception as exc:
            last_error = exc
            print(f"[{SERVICE_NAME}] Kafka not ready ({attempt}/60): {exc}")
            time.sleep(3)
    raise RuntimeError(f"Kafka consumer could not start: {last_error}")


def main():
    wait_for_opensearch()
    consumer = wait_for_kafka_consumer()
    for message in consumer:
        try:
            apply_event(message.value)
        except Exception as exc:
            print(f"[{SERVICE_NAME}] Failed to process message: {exc}")
            print(message.value)


if __name__ == "__main__":
    main()

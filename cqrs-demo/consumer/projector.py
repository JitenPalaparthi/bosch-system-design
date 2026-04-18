import json
import os
import time

from kafka import KafkaConsumer
from opensearchpy import OpenSearch


KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "dbserver1.public.products")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "product-projector-group")
OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST", "opensearch")
OPENSEARCH_PORT = int(os.getenv("OPENSEARCH_PORT", "9200"))
OPENSEARCH_INDEX = os.getenv("OPENSEARCH_INDEX", "products")


def wait_for_opensearch() -> OpenSearch:
    client = OpenSearch(
        hosts=[{"host": OPENSEARCH_HOST, "port": OPENSEARCH_PORT}],
        use_ssl=False,
        verify_certs=False,
        ssl_show_warn=False,
    )
    while True:
        try:
            if client.ping():
                return client
        except Exception:
            pass
        print("Waiting for OpenSearch...")
        time.sleep(5)


def ensure_index(client: OpenSearch):
    if client.indices.exists(index=OPENSEARCH_INDEX):
        return
    body = {
        "mappings": {
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "text"},
                "description": {"type": "text"},
                "price": {"type": "float"},
                "category": {"type": "keyword"},
                "created_at": {"type": "date"},
                "updated_at": {"type": "date"}
            }
        }
    }
    client.indices.create(index=OPENSEARCH_INDEX, body=body)
    print(f"Created index: {OPENSEARCH_INDEX}")


def wait_for_kafka() -> KafkaConsumer:
    while True:
        try:
            consumer = KafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                group_id=KAFKA_GROUP_ID,
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            )
            print(f"Connected to Kafka topic: {KAFKA_TOPIC}")
            return consumer
        except Exception as exc:
            print(f"Waiting for Kafka... {exc}")
            time.sleep(5)


def normalize_payload(record: dict):
    if "payload" in record:
        return record["payload"]
    return record


def main():
    os_client = wait_for_opensearch()
    ensure_index(os_client)
    consumer = wait_for_kafka()

    print("Projector started. Listening for Debezium CDC events...")
    for msg in consumer:
        event = normalize_payload(msg.value)
        op = event.get("op")
        after = event.get("after")
        before = event.get("before")

        print(f"Received event op={op}: {event}")

        try:
            if op in ("c", "r", "u") and after:
                document_id = after["id"]
                os_client.index(index=OPENSEARCH_INDEX, id=document_id, body=after, refresh=True)
                print(f"Indexed document id={document_id}")
            elif op == "d" and before:
                document_id = before["id"]
                os_client.delete(index=OPENSEARCH_INDEX, id=document_id, ignore=[404], refresh=True)
                print(f"Deleted document id={document_id}")
        except Exception as exc:
            print(f"Projection failure: {exc}")


if __name__ == "__main__":
    main()

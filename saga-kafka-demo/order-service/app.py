import json
import os
import sqlite3
import threading
import time
import uuid
from contextlib import closing
from datetime import datetime

from flask import Flask, jsonify, request
from kafka import KafkaAdminClient, KafkaConsumer, KafkaProducer
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError, NoBrokersAvailable

app = Flask(__name__)

SERVICE_NAME = os.getenv("SERVICE_NAME", "order-service")
PORT = int(os.getenv("FLASK_PORT", "8001"))
DB_PATH = os.getenv("ORDERS_DB_PATH", "/data/orders.db")
BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")
ORDER_CREATED_TOPIC = os.   getenv("ORDER_CREATED_TOPIC", "order.created")
PAYMENT_REQUESTED_TOPIC = os.getenv("PAYMENT_REQUESTED_TOPIC", "payment.requested")
PAYMENT_COMPLETED_TOPIC = os.getenv("PAYMENT_COMPLETED_TOPIC", "payment.completed")
PAYMENT_FAILED_TOPIC = os.getenv("PAYMENT_FAILED_TOPIC", "payment.failed")
ORDER_CANCELLED_TOPIC = os.getenv("ORDER_CANCELLED_TOPIC", "order.cancelled")

producer = None


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with closing(get_conn()) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                item TEXT NOT NULL,
                amount REAL NOT NULL,
                card_number TEXT,
                status TEXT NOT NULL,
                saga_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def wait_for_kafka(max_attempts=30, delay=2):
    global producer
    last_error = None

    for attempt in range(1, max_attempts + 1):
        try:
            p = KafkaProducer(
                bootstrap_servers=BOOTSTRAP,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                key_serializer=lambda v: v.encode("utf-8") if v else None,
            )

            if p.bootstrap_connected():
                producer = p
                print(f"[{SERVICE_NAME}] Connected to Kafka at {BOOTSTRAP}")
                return

            p.close()
            print(f"[{SERVICE_NAME}] Kafka socket open but bootstrap not ready (attempt {attempt}/{max_attempts})")

        except Exception as e:
            last_error = e
            print(f"[{SERVICE_NAME}] Kafka not ready yet (attempt {attempt}/{max_attempts}): {e}")

        time.sleep(delay)

    raise RuntimeError(f"Kafka broker is not available at {BOOTSTRAP}. Last error: {last_error}")

def create_topics():
    admin = KafkaAdminClient(bootstrap_servers=BOOTSTRAP)
    topics = [
        NewTopic(name=ORDER_CREATED_TOPIC, num_partitions=3, replication_factor=1),
        NewTopic(name=PAYMENT_REQUESTED_TOPIC, num_partitions=3, replication_factor=1),
        NewTopic(name=PAYMENT_COMPLETED_TOPIC, num_partitions=3, replication_factor=1),
        NewTopic(name=PAYMENT_FAILED_TOPIC, num_partitions=3, replication_factor=1),
        NewTopic(name=ORDER_CANCELLED_TOPIC, num_partitions=3, replication_factor=1),
    ]
    try:
        admin.create_topics(new_topics=topics, validate_only=False)
    except TopicAlreadyExistsError:
        pass
    finally:
        admin.close()


def update_order_status(order_id, status):
    now = datetime.utcnow().isoformat()
    with closing(get_conn()) as conn:
        conn.execute(
            "UPDATE orders SET status = ?, updated_at = ? WHERE order_id = ?",
            (status, now, order_id),
        )
        conn.commit()


def fetch_order(order_id):
    with closing(get_conn()) as conn:
        row = conn.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,)).fetchone()
        return dict(row) if row else None


def list_orders():
    with closing(get_conn()) as conn:
        rows = conn.execute("SELECT * FROM orders ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]


def publish(topic, key, payload):
    producer.send(topic, key=key, value=payload)
    producer.flush()
    print(f"[{SERVICE_NAME}] Published to {topic}: {payload}")


def start_payment_event_consumer():
    def run():
        consumer = KafkaConsumer(
            PAYMENT_COMPLETED_TOPIC,
            PAYMENT_FAILED_TOPIC,
            bootstrap_servers=BOOTSTRAP,
            group_id="order-service-saga-group",
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            key_deserializer=lambda m: m.decode("utf-8") if m else None,
        )
        print(f"[{SERVICE_NAME}] Listening for payment results...")
        for message in consumer:
            event = message.value
            order_id = event["order_id"]
            saga_id = event["saga_id"]
            if message.topic == PAYMENT_COMPLETED_TOPIC:
                update_order_status(order_id, "CONFIRMED")
                print(f"[{SERVICE_NAME}] Saga {saga_id}: payment successful, order confirmed")
            elif message.topic == PAYMENT_FAILED_TOPIC:
                update_order_status(order_id, "CANCELLED")
                compensation_event = {
                    "event_type": "ORDER_CANCELLED",
                    "saga_id": saga_id,
                    "order_id": order_id,
                    "reason": event.get("reason", "payment_failed"),
                    "timestamp": datetime.utcnow().isoformat(),
                }
                publish(ORDER_CANCELLED_TOPIC, order_id, compensation_event)
                print(f"[{SERVICE_NAME}] Saga {saga_id}: payment failed, compensation executed")

    thread = threading.Thread(target=run, daemon=True)
    thread.start()


@app.get("/health")
def health():
    return jsonify({"status": "UP", "service": SERVICE_NAME})


@app.get("/orders")
def get_orders():
    return jsonify(list_orders())


@app.get("/orders/<order_id>")
def get_order(order_id):
    order = fetch_order(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(order)


@app.post("/orders")
def create_order():
    payload = request.get_json(force=True)
    customer_id = payload.get("customer_id")
    item = payload.get("item")
    amount = payload.get("amount")
    card_number = payload.get("card_number", "")

    if not customer_id or not item or amount is None:
        return jsonify({"error": "customer_id, item and amount are required"}), 400

    order_id = str(uuid.uuid4())
    saga_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    with closing(get_conn()) as conn:
        conn.execute(
            """
            INSERT INTO orders(order_id, customer_id, item, amount, card_number, status, saga_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (order_id, customer_id, item, float(amount), card_number, "PENDING", saga_id, now, now),
        )
        conn.commit()

    order_created = {
        "event_type": "ORDER_CREATED",
        "saga_id": saga_id,
        "order_id": order_id,
        "customer_id": customer_id,
        "item": item,
        "amount": float(amount),
        "timestamp": now,
    }
    payment_requested = {
        "event_type": "PAYMENT_REQUESTED",
        "saga_id": saga_id,
        "order_id": order_id,
        "customer_id": customer_id,
        "amount": float(amount),
        "card_number": card_number,
        "timestamp": now,
    }

    publish(ORDER_CREATED_TOPIC, order_id, order_created)
    publish(PAYMENT_REQUESTED_TOPIC, order_id, payment_requested)

    return jsonify(
        {
            "message": "Order accepted and saga started",
            "order_id": order_id,
            "saga_id": saga_id,
            "status": "PENDING",
            "next_step": "payment-service will approve or reject the payment",
        }
    ), 202


if __name__ == "__main__":
    init_db()
    wait_for_kafka()
    create_topics()
    start_payment_event_consumer()
    app.run(host="0.0.0.0", port=PORT, debug=False)

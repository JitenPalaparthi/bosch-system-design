import json
import os
import random
import sqlite3
import threading
import time
from contextlib import closing
from datetime import datetime

from flask import Flask, jsonify
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import NoBrokersAvailable

app = Flask(__name__)

SERVICE_NAME = os.getenv("SERVICE_NAME", "payment-service")
PORT = int(os.getenv("FLASK_PORT", "8002"))
DB_PATH = os.getenv("PAYMENTS_DB_PATH", "/data/payments.db")
BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
PAYMENT_REQUESTED_TOPIC = os.getenv("PAYMENT_REQUESTED_TOPIC", "payment.requested")
PAYMENT_COMPLETED_TOPIC = os.getenv("PAYMENT_COMPLETED_TOPIC", "payment.completed")
PAYMENT_FAILED_TOPIC = os.getenv("PAYMENT_FAILED_TOPIC", "payment.failed")

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
            CREATE TABLE IF NOT EXISTS payments (
                payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT NOT NULL,
                saga_id TEXT NOT NULL,
                amount REAL NOT NULL,
                status TEXT NOT NULL,
                reason TEXT,
                created_at TEXT NOT NULL
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

def save_payment(order_id, saga_id, amount, status, reason=None):
    with closing(get_conn()) as conn:
        conn.execute(
            """
            INSERT INTO payments(order_id, saga_id, amount, status, reason, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (order_id, saga_id, float(amount), status, reason, datetime.utcnow().isoformat()),
        )
        conn.commit()


def list_payments():
    with closing(get_conn()) as conn:
        rows = conn.execute("SELECT * FROM payments ORDER BY payment_id DESC").fetchall()
        return [dict(r) for r in rows]


def publish(topic, key, payload):
    producer.send(topic, key=key, value=payload)
    producer.flush()
    print(f"[{SERVICE_NAME}] Published to {topic}: {payload}")


def evaluate_payment(event):
    card_number = str(event.get("card_number", ""))
    amount = float(event["amount"])

    if card_number.endswith("0000"):
        return False, "card_declined_demo_rule"
    if amount > 1000:
        return False, "amount_exceeds_demo_limit"
    if random.random() < 0.1:
        return False, "random_demo_failure"
    return True, None


def start_payment_request_consumer():
    def run():
        consumer = KafkaConsumer(
            PAYMENT_REQUESTED_TOPIC,
            bootstrap_servers=BOOTSTRAP,
            group_id="payment-service-group",
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            key_deserializer=lambda m: m.decode("utf-8") if m else None,
        )
        print(f"[{SERVICE_NAME}] Listening for payment requests...")
        for message in consumer:
            event = message.value
            order_id = event["order_id"]
            saga_id = event["saga_id"]
            approved, reason = evaluate_payment(event)
            time.sleep(1)

            if approved:
                save_payment(order_id, saga_id, event["amount"], "APPROVED")
                payment_completed = {
                    "event_type": "PAYMENT_COMPLETED",
                    "saga_id": saga_id,
                    "order_id": order_id,
                    "amount": float(event["amount"]),
                    "timestamp": datetime.utcnow().isoformat(),
                }
                publish(PAYMENT_COMPLETED_TOPIC, order_id, payment_completed)
            else:
                save_payment(order_id, saga_id, event["amount"], "FAILED", reason)
                payment_failed = {
                    "event_type": "PAYMENT_FAILED",
                    "saga_id": saga_id,
                    "order_id": order_id,
                    "amount": float(event["amount"]),
                    "reason": reason,
                    "timestamp": datetime.utcnow().isoformat(),
                }
                publish(PAYMENT_FAILED_TOPIC, order_id, payment_failed)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()


@app.get("/health")
def health():
    return jsonify({"status": "UP", "service": SERVICE_NAME})


@app.get("/payments")
def get_payments():
    return jsonify(list_payments())


if __name__ == "__main__":
    init_db()
    wait_for_kafka()
    start_payment_request_consumer()
    app.run(host="0.0.0.0", port=PORT, debug=False)

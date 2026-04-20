import os
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone

import psycopg
from flask import Flask, jsonify, request

app = Flask(__name__)

SERVICE_NAME = os.getenv("SERVICE_NAME", "command-service")
PORT = int(os.getenv("FLASK_PORT", "8001"))
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://appuser:apppass@postgres:5432/ordersdb")


@contextmanager
def get_conn():
    conn = psycopg.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@app.get("/health")
def health():
    return jsonify({"status": "UP", "service": SERVICE_NAME})


@app.post("/orders")
def create_order():
    payload = request.get_json(force=True)
    required = ["customer_id", "customer_name", "item", "quantity", "price"]
    missing = [field for field in required if payload.get(field) in (None, "")]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    order_id = str(uuid.uuid4())
    now = utcnow_iso()

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO orders (
                    order_id, customer_id, customer_name, item, quantity, price, status, created_at, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING order_id, customer_id, customer_name, item, quantity, price, status, tracking_id, created_at, updated_at
                """,
                (
                    order_id,
                    payload["customer_id"],
                    payload["customer_name"],
                    payload["item"],
                    int(payload["quantity"]),
                    float(payload["price"]),
                    "CREATED",
                    now,
                    now,
                ),
            )
            row = cur.fetchone()
        conn.commit()

    return (
        jsonify(
            {
                "message": "Order created on write side; Debezium will publish CDC event to Kafka",
                "order": row_to_dict(row),
            }
        ),
        201,
    )


@app.post("/orders/<order_id>/cancel")
def cancel_order(order_id: str):
    payload = request.get_json(silent=True) or {}
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT status FROM orders WHERE order_id = %s", (order_id,))
            current = cur.fetchone()
            if not current:
                return jsonify({"error": "Order not found"}), 404
            if current[0] == "SHIPPED":
                return jsonify({"error": "Shipped orders cannot be cancelled"}), 409

            cur.execute(
                """
                UPDATE orders
                SET status = %s, updated_at = NOW()
                WHERE order_id = %s
                RETURNING order_id, customer_id, customer_name, item, quantity, price, status, tracking_id, created_at, updated_at
                """,
                ("CANCELLED", order_id),
            )
            row = cur.fetchone()
        conn.commit()

    return jsonify({"message": payload.get("reason", "Order cancelled"), "order": row_to_dict(row)})


@app.post("/orders/<order_id>/ship")
def ship_order(order_id: str):
    payload = request.get_json(force=True)
    tracking_id = payload.get("tracking_id")
    if not tracking_id:
        return jsonify({"error": "tracking_id is required"}), 400

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT status FROM orders WHERE order_id = %s", (order_id,))
            current = cur.fetchone()
            if not current:
                return jsonify({"error": "Order not found"}), 404
            if current[0] == "CANCELLED":
                return jsonify({"error": "Cancelled orders cannot be shipped"}), 409

            cur.execute(
                """
                UPDATE orders
                SET status = %s, tracking_id = %s, updated_at = NOW()
                WHERE order_id = %s
                RETURNING order_id, customer_id, customer_name, item, quantity, price, status, tracking_id, created_at, updated_at
                """,
                ("SHIPPED", tracking_id, order_id),
            )
            row = cur.fetchone()
        conn.commit()

    return jsonify({"message": "Order shipped", "order": row_to_dict(row)})


@app.get("/orders-write")
def list_orders_write_side():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT order_id, customer_id, customer_name, item, quantity, price, status, tracking_id, created_at, updated_at
                FROM orders
                ORDER BY created_at DESC
                """
            )
            rows = cur.fetchall()

    return jsonify([row_to_dict(row) for row in rows])


def row_to_dict(row):
    if row is None:
        return None
    return {
        "order_id": str(row[0]),
        "customer_id": row[1],
        "customer_name": row[2],
        "item": row[3],
        "quantity": row[4],
        "price": float(row[5]),
        "status": row[6],
        "tracking_id": row[7],
        "created_at": row[8].isoformat() if hasattr(row[8], "isoformat") else str(row[8]),
        "updated_at": row[9].isoformat() if hasattr(row[9], "isoformat") else str(row[9]),
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=False)

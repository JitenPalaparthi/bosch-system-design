
import os, uuid, logging
from decimal import Decimal, InvalidOperation

from flask import Flask, request, jsonify
from dotenv import load_dotenv

from db import init_db, insert_order
from kafka_io import make_producer, ORDERS_TOPIC

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
log = logging.getLogger("orders_api")

PORT = int(os.getenv("PORT", "8000"))

app = Flask(__name__)

# init db and kafka producer at startup
init_db()
producer = make_producer()

def _coerce_price(p):
    try:
        return float(p)
    except (TypeError, ValueError, InvalidOperation):
        raise ValueError("price must be a number")

@app.post("/orders")
def create_order():
    data = request.get_json(force=True, silent=False) or {}
    for f in ("name","item","price","quantity"):
        if f not in data:
            return jsonify(ok=False, error=f"missing field '{f}'"), 400

    try:
        price = _coerce_price(data["price"])
        quantity = int(data["quantity"])
        if quantity <= 0:
            return jsonify(ok=False, error="quantity must be > 0"), 400
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 400

    order = {
        "id": str(uuid.uuid4()),
        "name": str(data["name"]),
        "item": str(data["item"]),
        "price": price,
        "quantity": quantity,
    }

    # 1) store to Postgres
    row = insert_order(order)

    # send email

    # send sms 

    # notify user

    # 2) produce to Kafka topic
    future = producer.send(ORDERS_TOPIC, key=order["id"], value=row)
    meta = future.get(timeout=10)
    log.info("Produced order %s -> %s[%s@%s]", order["id"], meta.topic, meta.partition, meta.offset)

    return jsonify(ok=True, order=row), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)

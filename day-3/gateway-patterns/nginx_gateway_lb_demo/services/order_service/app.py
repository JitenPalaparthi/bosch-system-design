import os
from flask import Flask, jsonify

app = Flask(__name__)
INSTANCE_NAME = os.getenv("INSTANCE_NAME", "order-service-unknown")

ORDERS = [
    {"id": 1001, "item": "Laptop"},
    {"id": 1002, "item": "Mouse"},
]

@app.get("/orders")
def list_orders():
    return jsonify({
        "service": "order-service",
        "instance": INSTANCE_NAME,
        "orders": ORDERS
    })

@app.get("/<order_id>")
def get_order(order_id):
    return jsonify({
        "service": "order-service",
        "instance": INSTANCE_NAME,
        "order": {
            "id": int(order_id),
            "item": f"Item-{order_id}"
        }
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)

import os
from flask import Flask, jsonify

app = Flask(__name__)
INSTANCE_NAME = os.getenv("INSTANCE_NAME", "user-service-unknown")

USERS = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
]

@app.get("/users")
def list_users():
    return jsonify({
        "service": "user-service",
        "instance": INSTANCE_NAME,
        "users": USERS
    })

@app.get("/<user_id>")
def get_user(user_id):
    return jsonify({
        "service": "user-service",
        "instance": INSTANCE_NAME,
        "user": {
            "id": int(user_id),
            "name": f"User-{user_id}"
        }
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)

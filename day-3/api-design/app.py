from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, asdict
from typing import Dict, List

from flask import Flask, jsonify, g, request

app = Flask(__name__)


@dataclass
class User:
    id: int
    name: str
    email: str


USERS: Dict[int, User] = {
    1: User(id=1, name="Alice", email="alice@example.com"),
    2: User(id=2, name="Bob", email="bob@example.com"),
    3: User(id=3, name="Charlie", email="charlie@example.com"),
}
NEXT_ID = 4
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@app.before_request
def attach_request_id() -> None:
    g.request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))


@app.after_request
def add_response_headers(response):
    response.headers["X-Request-ID"] = g.request_id
    response.headers["Content-Type"] = "application/json"
    return response



def success(data, status: int = 200, meta: dict | None = None):
    payload = {
        "data": data,
        "meta": {
            "requestId": g.request_id,
        },
    }
    if meta:
        payload["meta"].update(meta)
    return jsonify(payload), status



def error(code: str, message: str, status: int, details: dict | None = None):
    payload = {
        "error": {
            "code": code,
            "message": message,
        },
        "meta": {
            "requestId": g.request_id,
        },
    }
    if details:
        payload["error"]["details"] = details
    return jsonify(payload), status



def validate_user_payload(payload: dict, partial: bool = False) -> List[str]:
    errors: List[str] = []

    if not partial or "name" in payload:
        name = payload.get("name")
        if not isinstance(name, str) or not name.strip():
            errors.append("name is required and must be a non-empty string")

    if not partial or "email" in payload:
        email = payload.get("email")
        if not isinstance(email, str) or not EMAIL_RE.match(email):
            errors.append("email is required and must be a valid email address")

    return errors


@app.get("/health")
def health():
    return success({"status": "ok"})


@app.get("/v1/users")
def list_users():
    search = request.args.get("search", "").strip().lower()

    try:
        page = max(1, int(request.args.get("page", 1)))
        limit = max(1, min(100, int(request.args.get("limit", 10))))
    except ValueError:
        return error("INVALID_PAGINATION", "page and limit must be integers", 400)

    users = list(USERS.values())
    if search:
        users = [
            u for u in users
            if search in u.name.lower() or search in u.email.lower()
        ]

    total = len(users)
    start = (page - 1) * limit
    end = start + limit
    page_items = [asdict(u) for u in users[start:end]]

    return success(
        page_items,
        meta={
            "page": page,
            "limit": limit,
            "total": total,
        },
    )


@app.get("/v1/users/<int:user_id>")
def get_user(user_id: int):
    user = USERS.get(user_id)
    if not user:
        return error("USER_NOT_FOUND", f"User {user_id} does not exist", 404)
    return success(asdict(user))


@app.post("/v1/users")
def create_user():
    global NEXT_ID

    payload = request.get_json(silent=True)
    if payload is None:
        return error("INVALID_JSON", "Request body must be valid JSON", 400)

    errors = validate_user_payload(payload)
    if errors:
        return error("VALIDATION_FAILED", "Invalid request body", 422, {"issues": errors})

    email = payload["email"].strip().lower()
    if any(u.email.lower() == email for u in USERS.values()):
        return error("EMAIL_ALREADY_EXISTS", f"Email '{email}' already exists", 409)

    user = User(id=NEXT_ID, name=payload["name"].strip(), email=email)
    USERS[NEXT_ID] = user
    NEXT_ID += 1

    return success(asdict(user), status=201)


@app.put("/v1/users/<int:user_id>")
def replace_user(user_id: int):
    payload = request.get_json(silent=True)
    if payload is None:
        return error("INVALID_JSON", "Request body must be valid JSON", 400)

    if user_id not in USERS:
        return error("USER_NOT_FOUND", f"User {user_id} does not exist", 404)

    errors = validate_user_payload(payload)
    if errors:
        return error("VALIDATION_FAILED", "Invalid request body", 422, {"issues": errors})

    email = payload["email"].strip().lower()
    for existing_id, existing_user in USERS.items():
        if existing_id != user_id and existing_user.email.lower() == email:
            return error("EMAIL_ALREADY_EXISTS", f"Email '{email}' already exists", 409)

    USERS[user_id] = User(id=user_id, name=payload["name"].strip(), email=email)
    return success(asdict(USERS[user_id]))


@app.patch("/v1/users/<int:user_id>")
def patch_user(user_id: int):
    payload = request.get_json(silent=True)
    if payload is None:
        return error("INVALID_JSON", "Request body must be valid JSON", 400)

    user = USERS.get(user_id)
    if not user:
        return error("USER_NOT_FOUND", f"User {user_id} does not exist", 404)

    allowed_fields = {"name", "email"}
    unknown_fields = set(payload.keys()) - allowed_fields
    if unknown_fields:
        return error(
            "UNKNOWN_FIELDS",
            "Request body contains unsupported fields",
            400,
            {"fields": sorted(unknown_fields)},
        )

    errors = validate_user_payload(payload, partial=True)
    if errors:
        return error("VALIDATION_FAILED", "Invalid request body", 422, {"issues": errors})

    if "name" in payload:
        user.name = payload["name"].strip()

    if "email" in payload:
        email = payload["email"].strip().lower()
        for existing_id, existing_user in USERS.items():
            if existing_id != user_id and existing_user.email.lower() == email:
                return error("EMAIL_ALREADY_EXISTS", f"Email '{email}' already exists", 409)
        user.email = email

    return success(asdict(user))


@app.delete("/v1/users/<int:user_id>")
def delete_user(user_id: int):
    if user_id not in USERS:
        return error("USER_NOT_FOUND", f"User {user_id} does not exist", 404)

    del USERS[user_id]
    return success({"deleted": True, "id": user_id})


@app.errorhandler(404)
def handle_404(_):
    return error("ENDPOINT_NOT_FOUND", "The requested endpoint does not exist", 404)


@app.errorhandler(405)
def handle_405(_):
    return error("METHOD_NOT_ALLOWED", "HTTP method not allowed for this endpoint", 405)


@app.errorhandler(500)
def handle_500(_):
    return error("INTERNAL_SERVER_ERROR", "An unexpected server error occurred", 500)


if __name__ == "__main__":
    app.run(debug=True)

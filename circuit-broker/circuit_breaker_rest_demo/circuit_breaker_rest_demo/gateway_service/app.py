import os
from typing import Any

import requests
from flask import Flask, jsonify

from breaker import CircuitBreaker, CircuitBreakerOpenError

app = Flask(__name__)

PORT = int(os.getenv("PORT", "5000"))
DOWNSTREAM_URL = os.getenv("DOWNSTREAM_URL", "http://localhost:5001/work")
FAILURE_THRESHOLD = int(os.getenv("FAILURE_THRESHOLD", "3"))
RECOVERY_TIMEOUT = float(os.getenv("RECOVERY_TIMEOUT", "8"))
SUCCESS_THRESHOLD = int(os.getenv("SUCCESS_THRESHOLD", "2"))
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "2"))

breaker = CircuitBreaker(
    failure_threshold=FAILURE_THRESHOLD,
    recovery_timeout=RECOVERY_TIMEOUT,
    success_threshold=SUCCESS_THRESHOLD,
)


def call_downstream() -> dict[str, Any]:
    response = requests.get(DOWNSTREAM_URL, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


@app.get("/health")
def health():
    return jsonify({"service": "gateway-service", "status": "up"})


@app.get("/breaker")
def breaker_state():
    return jsonify(breaker.stats())


@app.get("/proxy")
def proxy():
    try:
        data = breaker.call(call_downstream)
        return jsonify(
            {
                "success": True,
                "breaker_state": breaker.stats()["state"],
                "downstream": data,
            }
        )
    except CircuitBreakerOpenError:
        return jsonify(
            {
                "success": False,
                "breaker_state": breaker.stats()["state"],
                "message": "Fallback response because circuit is open",
            }
        ), 503
    except requests.RequestException as exc:
        return jsonify(
            {
                "success": False,
                "breaker_state": breaker.stats()["state"],
                "message": "Downstream request failed",
                "error": str(exc),
            }
        ), 502
    except Exception as exc:
        return jsonify(
            {
                "success": False,
                "breaker_state": breaker.stats()["state"],
                "message": "Unexpected error",
                "error": str(exc),
            }
        ), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=False)

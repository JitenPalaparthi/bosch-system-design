import os
import random
from flask import Flask, jsonify

app = Flask(__name__)

PORT = int(os.getenv("PORT", "5001"))
FAILURE_RATE = float(os.getenv("FAILURE_RATE", "0.7"))


@app.get("/health")
def health():
    return jsonify({"service": "flaky-service", "status": "up"})


@app.get("/work")
def work():
    if random.random() < FAILURE_RATE:
        return jsonify(
            {
                "service": "flaky-service",
                "success": False,
                "message": "Random failure occurred"
            }
        ), 500

    return jsonify(
        {
            "service": "flaky-service",
            "success": True,
            "message": "Work completed"
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=False)

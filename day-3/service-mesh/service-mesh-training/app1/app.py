from flask import Flask, jsonify
import os
import requests
import time

app = Flask(__name__)
TARGET_URL = os.getenv('TARGET_URL', 'http://envoy1:15001/hello')

@app.get('/')
def index():
    return jsonify({
        'service': 'app1',
        'message': 'app1 is running',
        'next_hop': TARGET_URL,
    })

@app.get('/call')
def call_app2():
    start = time.time()
    try:
        response = requests.get(TARGET_URL, timeout=4)
        elapsed_ms = round((time.time() - start) * 1000, 2)
        return jsonify({
            'service': 'app1',
            'called_via': 'envoy1 -> envoy2 -> app2',
            'status_code_from_target': response.status_code,
            'elapsed_ms': elapsed_ms,
            'target_response': response.json() if 'application/json' in response.headers.get('content-type', '') else response.text,
        }), response.status_code
    except Exception as exc:
        elapsed_ms = round((time.time() - start) * 1000, 2)
        return jsonify({
            'service': 'app1',
            'error': str(exc),
            'elapsed_ms': elapsed_ms,
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

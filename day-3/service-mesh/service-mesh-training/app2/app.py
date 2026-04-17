from flask import Flask, jsonify
import os
import random
import socket
import time

app = Flask(__name__)
FAILURE_RATE = int(os.getenv('FAILURE_RATE', '0'))
DELAY_MS = int(os.getenv('DELAY_MS', '0'))

@app.get('/')
def index():
    return jsonify({
        'service': 'app2',
        'message': 'app2 is running',
    })

@app.get('/hello')
def hello():
    if DELAY_MS > 0:
        time.sleep(DELAY_MS / 1000)

    if FAILURE_RATE > 0 and random.randint(1, 100) <= FAILURE_RATE:
        return jsonify({
            'service': 'app2',
            'status': 'temporary failure',
            'hostname': socket.gethostname(),
            'delay_ms': DELAY_MS,
            'failure_rate_percent': FAILURE_RATE,
        }), 500

    return jsonify({
        'service': 'app2',
        'status': 'ok',
        'hostname': socket.gethostname(),
        'epoch_time': time.time(),
        'delay_ms': DELAY_MS,
        'failure_rate_percent': FAILURE_RATE,
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

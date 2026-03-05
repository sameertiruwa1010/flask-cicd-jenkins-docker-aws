from flask import Flask, jsonify, request
import os
import socket
import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'message': 'Hello from Flask CI/CD Pipeline!',
        'hostname': socket.gethostname(),
        'version': '1.0.0',
        'timestamp': datetime.datetime.now().isoformat(),
        'environment': os.getenv('FLASK_ENV', 'production')
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

@app.route('/api/echo', methods=['POST'])
def echo():
    data = request.get_json()
    return jsonify({
        'received': data,
        'echo': 'success'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

import base64
import hashlib
import json
import time
from flask import Flask, request, jsonify
from collections import OrderedDict

app = Flask(__name__)

def solve_challenge(challenge, salt, algorithm='SHA-256', maxnumber=100000, start=0):
    algo = algorithm.replace('-', '').lower()
    if algo not in hashlib.algorithms_available:
        raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    hasher = getattr(hashlib, algo)
    for number in range(start, maxnumber + 1):
        data = (salt + str(number)).encode()
        digest = hasher(data).hexdigest()
        if digest == challenge:
            return number
    return None

@app.route('/solve', methods=['POST'])
def solve():
    try:
        data = request.get_json(force=True)
        challenge = data['challenge']
        salt = data['salt']
        algorithm = data.get('algorithm', 'SHA-256')
        signature = data.get('signature')
        maxnumber = int(data.get('maxnumber', 100000))

        start_time = time.time()
        number = solve_challenge(challenge, salt, algorithm, maxnumber)
        took = int((time.time() - start_time) * 1000)

        if number is None:
            return jsonify({"error": "No valid solution found"}), 400

        result = OrderedDict()
        result["algorithm"] = algorithm
        result["challenge"] = challenge
        result["number"] = number
        result["salt"] = salt
        result["signature"] = signature
        result["took"] = took

        token = base64.b64encode(json.dumps(result, separators=(',', ':')).encode()).decode()

        return jsonify({
            "token": token,
            "solution": result
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)
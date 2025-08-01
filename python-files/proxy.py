from flask import Flask, request, Response
import requests
import os
from datetime import datetime

app = Flask(__name__)

# Point to the real backend server (Machine B)
REAL_SERVER = "http://192.168.1.4:2020"

# Folder to store request logs
LOG_FOLDER = "logs"
os.makedirs(LOG_FOLDER, exist_ok=True)

@app.route('/', defaults={'path': ''}, methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"])
@app.route('/<path:path>', methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"])
def proxy(path):
    full_url = f"{REAL_SERVER}/{path}"

    method = request.method
    headers = {k: v for k, v in request.headers if k.lower() != 'host'}
    data = request.get_data()
    params = request.args

    # Log file with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    log_file = os.path.join(LOG_FOLDER, f"log_{timestamp}.txt")

    try:
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"--- INCOMING REQUEST ---\n")
            f.write(f"URL: {full_url}\n")
            f.write(f"Method: {method}\n")
            f.write(f"Headers: {headers}\n")
            f.write(f"Query Params: {params.to_dict()}\n")
            f.write(f"Body:\n{data.decode('utf-8', errors='ignore')}\n")

        # Forward request with appropriate method
        resp = requests.request(
            method=method,
            url=full_url,
            headers=headers,
            params=params,
            data=data,
            cookies=request.cookies,
            allow_redirects=False,
            timeout=15  # prevent hanging
        )

        # Relay response
        response = Response(resp.content, resp.status_code)
        for key, value in resp.headers.items():
            response.headers[key] = value

        return response

    except requests.exceptions.RequestException as e:
        # Log the error
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n--- ERROR ---\n{str(e)}\n")
        return f"Proxy Error: Failed to reach real server.\nDetails: {str(e)}", 502

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2020)

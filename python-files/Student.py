from flask import Flask, request
import os, threading, requests, socket, time
import subprocess

TEACHER_IP = "172.22.9.4"   # teacher PC’s IP
TEACHER_PORT = 8000
PC_NAME = socket.gethostname()
SECRET_KEY = "mysecret123"

app = Flask(__name__)

@app.route("/shutdown", methods=["POST"])
def shutdown():
    key = request.form.get("key")
    if key != SECRET_KEY:
        return "Unauthorized", 403
    # Run shutdown command with no window
    subprocess.run(
        ["shutdown", "/s", "/t", "0"],
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    return "Shutting down", 200

def register_with_teacher():
    while True:
        try:
            ip = socket.gethostbyname(socket.gethostname())
            requests.post(f"http://{TEACHER_IP}:{TEACHER_PORT}/register",
                          json={"name": PC_NAME, "ip": ip})
            print(f"Registered {PC_NAME} ({ip}) with teacher server")
        except Exception as e:
            print("Registration failed:", e)
        time.sleep(60)  # re-register every 60 sec

def run_server():
    app.run(host="0.0.0.0", port=5001, debug=False, use_reloader=False)

# Start threads
threading.Thread(target=register_with_teacher, daemon=True).start()
threading.Thread(target=run_server, daemon=True).start()

# Keep main thread alive
while True:
    time.sleep(3600)

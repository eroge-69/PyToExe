
import websocket
import json
import threading
import time

class QuotexClient:
    def __init__(self, email, password, asset="eur_usd", amount=100, duration=1, is_demo=True):
        self.email = email
        self.password = password
        self.asset = asset
        self.amount = amount
        self.duration = duration
        self.is_demo = is_demo
        self.token = None
        self.ws = None
        self.connected = False

    def on_open(self, ws):
        print("WebSocket opened. Logging in...")
        login_payload = {
            "msg_type": "login",
            "email": self.email,
            "password": self.password
        }
        self.send_message(login_payload)

    def on_message(self, ws, message):
        data = json.loads(message)
        print("Message Received:", data)

        if "msg_type" in data and data["msg_type"] == "login":
            if data.get("success"):
                self.token = data["token"]
                print(f"✅ Logged in! Token: {self.token}")
                self.connected = True
                self.subscribe_account()
            else:
                print("❌ Login failed:", data)

    def on_error(self, ws, error):
        print("WebSocket error:", error)

    def on_close(self, ws, close_status_code, close_msg):
        print("WebSocket closed:", close_status_code, close_msg)
        self.connected = False

    def send_message(self, payload):
        self.ws.send(json.dumps(payload))

    def subscribe_account(self):
        if self.token:
            self.send_message({
                "msg_type": "get_balance",
                "token": self.token,
                "demo": self.is_demo
            })

    def connect(self):
        websocket.enableTrace(False)
        self.ws = websocket.WebSocketApp(
            "wss://wss.quotex.io:443",
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        wst = threading.Thread(target=self.ws.run_forever)
        wst.daemon = True
        wst.start()

        timeout = 10
        while not self.connected and timeout:
            time.sleep(1)
            timeout -= 1
        if not self.connected:
            print("❌ Connection timeout or login failed.")

if __name__ == "__main__":
    quotex = QuotexClient(
        email="rkrohit301202@gmail.com",
        password="Rohitrohit30@",
        asset="usd/brl_otc",
        amount=100,
        duration=1,
        is_demo=True
    )
    quotex.connect()

    # Keep alive
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break

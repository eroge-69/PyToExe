import websocket
import threading
import time
import json
import uuid
import marketdata_pb2  # generated from .proto
import zlib

AUTH_TOKEN = "Bearer YOUR_ACCESS_TOKEN_HERE"
INSTRUMENT_KEYS = ["NSE_FO|45450"]  # Replace with desired symbol

def on_message(ws, message):
    try:
        decoded = marketdata_pb2.FeedMessage()
        decoded.ParseFromString(message)

        for key, data in decoded.feeds.items():
            if data.HasField("ltpc"):
                ltp = data.ltpc.ltp
                cp = data.ltpc.cp
                ltq = int(data.ltpc.ltq)
                print(f"{key} | LTP: {ltp} | CP: {cp} | LTQ: {ltq}")

                # Apply sample VSA + SMC logic
                if ltp > cp and ltq > 200:
                    print("[BUY ALERT]")
                elif ltp < cp and ltq > 200:
                    print("[SELL ALERT]")

    except Exception as e:
        print(f"Error decoding message: {e}")

def on_error(ws, error):
    print(f"WebSocket Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("WebSocket Closed")

def on_open(ws):
    print("WebSocket Opened")
    subscribe = {
        "guid": str(uuid.uuid4().hex),
        "method": "sub",
        "data": {
            "mode": "full",
            "instrumentKeys": INSTRUMENT_KEYS
        }
    }
    ws.send(json.dumps(subscribe), opcode=websocket.ABNF.OPCODE_BINARY)

def run_ws():
    ws_url = "wss://api-feed.upstox.com/v3/feed/market-data"
    headers = {
        "Authorization": AUTH_TOKEN,
        "Accept": "*/*"
    }

    ws = websocket.WebSocketApp(
        ws_url,
        header=[f"{k}: {v}" for k, v in headers.items()],
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open
    )
    ws.run_forever()

if __name__ == "__main__":
    run_ws()

from scapy.all import sniff, IP, TCP, UDP
import json
import websocket
import threading
import os
from dotenv import load_dotenv

load_dotenv()
# Replace this with your deployed WebSocket server's URL
SERVER_URL = os.getenv("VITE_BACKEND_URL")
if not SERVER_URL:
    print("Error: VITE_BACKEND_URL is not set in the environment or .env file.")
    input("Press Enter to exit...")
    exit(1)

def send_packet(ws, pkt):
    if pkt.haslayer(IP):
        data = {
            "src_ip": pkt[IP].src,
            "dst_ip": pkt[IP].dst,
            "protocol": (
                "TCP" if pkt.haslayer(TCP) else
                "UDP" if pkt.haslayer(UDP) else
                "Other"
            ),
            "size": len(pkt)
        }
        ws.send(json.dumps(data))

def start_sniff(ws):
    sniff(prn=lambda pkt: send_packet(ws, pkt), store=0)

def on_open(ws):
    print("[*] Connected to server. Capturing packets...")
    threading.Thread(target=start_sniff, args=(ws,), daemon=True).start()

def main():
    try:
        ws = websocket.WebSocketApp(SERVER_URL, on_open=on_open)
        ws.run_forever()
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()

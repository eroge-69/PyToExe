import socketio
import threading

SERVER_URL = "https://chat-2iqx.onrender.com"#input("🌐 Nhập link server (vd: http://localhost:10000 hoặc https://your-render.com): ")

sio = socketio.Client()

nickname = input("🔥 Nhập tên hiển thị: ")

@sio.event
def connect():
    print('🟢 Đã kết nối tới server!')

@sio.event
def message(data):
    print(f'{data}')

@sio.event
def disconnect():
    print('🔴 Mất kết nối tới server!')

def send_msg():
    while True:
        msg = input()
        if msg == "/exit":
            sio.disconnect()
            break
        if msg.strip() != "":
            sio.send(f'{nickname}: {msg}')

try:
    sio.connect(SERVER_URL)
    send_thread = threading.Thread(target=send_msg)
    send_thread.start()
except Exception as e:
    print(f"❌ Lỗi kết nối: {e}")

# client.py
import socket
import struct
import pickle
import tkinter as tk
from PIL import Image, ImageTk
import io
import time
import threading

SERVER_IP = "192.168.0.101"
PORT = 5051
AUTH_TOKEN = "secret-token"  # must match server

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((SERVER_IP, PORT))
# send token then wait for RES response
sock.sendall((AUTH_TOKEN + "\n").encode())
resp = b""
while b"\n" not in resp:
    resp += sock.recv(1024)
resp_line = resp.decode().strip()
if resp_line.startswith("AUTH_FAIL"):
    raise SystemExit("Authentication failed")
if not resp_line.startswith("RES:"):
    raise SystemExit("Bad handshake from server")
_, sw, sh = resp_line.split(":")
server_w, server_h = int(sw), int(sh)
print(f"[+] Server screen: {server_w}x{server_h}")

payload_size = struct.calcsize("Q")
data = b""

# Tkinter window
root = tk.Tk()
root.title("Remote Desktop")
label = tk.Label(root)
label.pack(fill=tk.BOTH, expand=True)

# Keep last send time to throttle mouse move
last_move = 0

def send_cmd(cmd: str):
    try:
        sock.sendall((cmd + "\n").encode())
    except Exception as e:
        print("[!] send_cmd error:", e)

def on_mouse_move(event):
    global last_move
    now = time.time()
    if now - last_move < 0.02:  # throttle
        return
    last_move = now
    # translate widget coords to server screen coords
    w = label.winfo_width()
    h = label.winfo_height()
    if w == 0 or h == 0:
        return
    sx = int(event.x * server_w / w)
    sy = int(event.y * server_h / h)
    send_cmd(f"mouse_move:{sx}:{sy}")

def on_button_press(event):
    btn = "left" if event.num == 1 else "right" if event.num == 3 else "middle"
    send_cmd(f"mouse_down:{btn}")

def on_button_release(event):
    btn = "left" if event.num == 1 else "right" if event.num == 3 else "middle"
    send_cmd(f"mouse_up:{btn}")
    # also send a click for compatibility
    send_cmd(f"mouse_click:{btn}")

def on_wheel(event):
    # delta sign: on Windows event.delta, on X11 use event.num
    delta = getattr(event, "delta", 0)
    if delta == 0:
        # fallback (Linux)
        if event.num == 4:
            delta = 120
        elif event.num == 5:
            delta = -120
    send_cmd(f"scroll:{int(delta/120*100)}")  # scale

def on_key_press(event):
    key = event.keysym
    # filter Shift/Control/Alt separately if needed
    send_cmd(f"key_down:{key}")

def on_key_release(event):
    key = event.keysym
    send_cmd(f"key_up:{key}")

label.bind("<Motion>", on_mouse_move)
label.bind("<ButtonPress>", on_button_press)
label.bind("<ButtonRelease>", on_button_release)
# wheel support
label.bind("<MouseWheel>", on_wheel)
label.bind("<Button-4>", on_wheel)
label.bind("<Button-5>", on_wheel)

root.bind("<KeyPress>", on_key_press)
root.bind("<KeyRelease>", on_key_release)
root.focus_set()

def receive_frames():
    global data
    try:
        while True:
            while len(data) < payload_size:
                packet = sock.recv(4*1024)
                if not packet:
                    print("[*] Server closed")
                    root.quit()
                    return
                data += packet
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("Q", packed_msg_size)[0]
            while len(data) < msg_size:
                data += sock.recv(4*1024)
            frame_data = data[:msg_size]
            data = data[msg_size:]
            img = pickle.loads(frame_data)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            pil_img = Image.open(buf)
            # Resize to fit label while keeping aspect
            w = label.winfo_width() or pil_img.width
            h = label.winfo_height() or pil_img.height
            pil_img = pil_img.resize((w, h), Image.BILINEAR)
            tk_img = ImageTk.PhotoImage(pil_img)
            label.config(image=tk_img)
            label.image = tk_img
    except Exception as e:
        print("[!] receive_frames ended:", e)
        root.quit()

# Run receiver in background
t = threading.Thread(target=receive_frames, daemon=True)
t.start()

root.mainloop()
sock.close()

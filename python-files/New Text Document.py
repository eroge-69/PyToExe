import socket
import threading
import tkinter as tk
import time
import sys
import os

running = False
sock = None
serial_file = None

# --- OSC helper ---
def osc_message(address, value):
    # OSC format: address\0 padded to 4 bytes, type tag string, then value
    def pad(s):
        return s + (b'\0' * ((4 - (len(s) % 4)) % 4))
    
    addr = pad(address.encode())
    tag = pad(b",f")  # float type
    val = pad(struct.pack(">f", value))
    return addr + tag + val

# --- Thread to read Micro:bit and send OSC ---
def bridge_loop(port_name, ip, port):
    global running, sock, serial_file
    try:
        # Open COM port as file
        if os.name == 'nt':  # Windows
            serial_file = open(rf"\\.\{port_name}", "rb", buffering=0)
        else:  # Linux/Mac
            serial_file = open(port_name, "rb", buffering=0)
    except Exception as e:
        status_var.set(f"Serial Error: {e}")
        running = False
        return
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    while running:
        try:
            line = serial_file.readline().decode(errors="ignore").strip()
            if not line:
                continue
            parts = line.split(",")
            if len(parts) != 5:
                continue
            ax, ay, az, btn_a, btn_b = map(int, parts)
            
            ax_norm = max(min(ax / 1024, 1), -1)
            ay_norm = max(min(ay / 1024, 1), -1)
            
            send_osc(ip, port, "/avatar/parameters/TiltX", ax_norm)
            send_osc(ip, port, "/avatar/parameters/TiltY", ay_norm)
            send_osc(ip, port, "/avatar/parameters/ButtonA", float(btn_a))
            send_osc(ip, port, "/avatar/parameters/ButtonB", float(btn_b))
            
            ax_var.set(f"{ax_norm:.2f}")
            ay_var.set(f"{ay_norm:.2f}")
            a_var.set(str(btn_a))
            b_var.set(str(btn_b))
        except Exception as e:
            status_var.set(f"Error: {e}")
            time.sleep(0.1)

def send_osc(ip, port, address, value):
    packet = b""
    packet += address.encode() + b"\0" * (4 - (len(address) % 4))
    packet += b",f\0\0"
    packet += struct.pack(">f", value)
    sock.sendto(packet, (ip, port))

# --- Start & Stop ---
def start_bridge():
    global running
    if running:
        return
    port_name = port_var.get()
    ip = ip_var.get()
    try:
        udp_port = int(port_num_var.get())
    except:
        status_var.set("Invalid port")
        return
    running = True
    status_var.set("Running...")
    threading.Thread(target=bridge_loop, args=(port_name, ip, udp_port), daemon=True).start()

def stop_bridge():
    global running, serial_file
    running = False
    if serial_file:
        serial_file.close()
        serial_file = None
    status_var.set("Stopped")

# --- GUI ---
root = tk.Tk()
root.title("Micro:bit → VRChat OSC Bridge (No Packages)")
root.geometry("400x300")

status_var = tk.StringVar(value="Stopped")
ax_var = tk.StringVar(value="0.00")
ay_var = tk.StringVar(value="0.00")
a_var = tk.StringVar(value="0")
b_var = tk.StringVar(value="0")

tk.Label(root, text="COM Port (e.g., COM3 or /dev/ttyACM0):").pack()
port_var = tk.StringVar()
tk.Entry(root, textvariable=port_var).pack()

tk.Label(root, text="VRChat IP:").pack()
ip_var = tk.StringVar(value="127.0.0.1")
tk.Entry(root, textvariable=ip_var).pack()

tk.Label(root, text="VRChat OSC Port:").pack()
port_num_var = tk.StringVar(value="9000")
tk.Entry(root, textvariable=port_num_var).pack()

tk.Button(root, text="Start", command=start_bridge).pack(pady=5)
tk.Button(root, text="Stop", command=stop_bridge).pack()

tk.Label(root, textvariable=status_var, fg="blue").pack(pady=5)
tk.Label(root, text="TiltX:").pack()
tk.Label(root, textvariable=ax_var).pack()
tk.Label(root, text="TiltY:").pack()
tk.Label(root, textvariable=ay_var).pack()
tk.Label(root, text="Button A:").pack()
tk.Label(root, textvariable=a_var).pack()
tk.Label(root, text="Button B:").pack()
tk.Label(root, textvariable=b_var).pack()

root.mainloop()

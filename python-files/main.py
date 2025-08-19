import socket
import pyvjoy

UDP_PORT = 4210
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("", UDP_PORT))  # Listen on all interfaces

j = pyvjoy.VJoyDevice(1)  # vJoy device ID 1

print("Handbrake receiver running... Press Ctrl+C to exit.")

while True:
    data, _ = sock.recvfrom(1024)
    try:
        percent = int(data.decode().strip())
        scaled = int((percent / 100.0) * 32767)
        j.set_axis(pyvjoy.HID_USAGE_Z, scaled)
    except:
        pass

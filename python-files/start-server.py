import socket

def send_wol(mac):
    mac_bytes = bytes.fromhex(mac.replace(":", ""))
    packet = b'\xff' * 6 + mac_bytes * 16
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(packet, ("51.14.188.241", 9))

send_wol("e8:40:f2:c3:07:5b")
print("Start up packet sent")

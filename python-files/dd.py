import socket
import requests

def get_public_ip():
    try:
        ip = requests.get("https://api.ipify.org").text
        print("Public IP tapıldı:", ip)
        return ip
    except:
        return "IP tapılmadı"

def client():
    try:
        # Əvvəlcə serverə qoşul
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        SERVER_IP = "212.47.142.103"  # <- BURADA server IP-ni yaz: LAN varsa lokal IP, uzaqdansa public IP
        PORT = 4444

        s.connect((SERVER_IP, PORT))

        # İP tap və göndər
        ip = get_public_ip()
        s.send(ip.encode())

        # Gözləyir...
        response = s.recv(1024)
        print("Serverdən cavab:", response.decode())

        s.close()
    except Exception as e:
        print("Xəta baş verdi:", e)

client()

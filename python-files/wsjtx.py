import socket
import threading
from pystray import Icon, Menu, MenuItem
from PIL import Image
import os
import sys

def start_server():
    host = '127.0.0.1'
    port = 2232
    filename = 'C:/test.adi'

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Server listening on {host}:{port}")

        while True:
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    with open(filename, 'ab') as f:
                        f.write(data)
                    print(f"Received: {data.decode()}")

def kill_process(icon):
    os._exit(0)

def main():
    # Create system tray icon
    image = Image.new('RGB', (64, 64), color = (73, 109, 137))
    menu = Menu(
        MenuItem('Kill Process', lambda icon: kill_process(icon))
    )
    icon = Icon("Server", image, menu=menu)

    # Start server in separate thread
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True  # Allow program to exit even if thread is still running
    server_thread.start()

    # Run system tray icon
    icon.run()

if __name__ == "__main__":
    main()
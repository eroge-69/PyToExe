
import socket
import cv2
import pickle
import struct
import pyautogui
import numpy as np

def main():
    server_ip = input("Receiver (Laptop) IP address daalein: ")
    port = 9999

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, port))
    print(f"[Connected] Streaming to {server_ip}:{port}")

    try:
        while True:
            screenshot = pyautogui.screenshot()
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGR2RGB)
            result, frame = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
            data = pickle.dumps(frame)
            message = struct.pack("Q", len(data)) + data
            client_socket.sendall(message)
    except KeyboardInterrupt:
        print("Stopped by user")
    finally:
        client_socket.close()

if __name__ == "__main__":
    main()

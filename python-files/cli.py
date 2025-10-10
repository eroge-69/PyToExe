import cv2
import socket
import numpy as np

def main():
    host = '127.0.0.1'
    port = 12345

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    while True:
        data = b""
        while True:
            packet = client_socket.recv(4096)
            if not packet:
                break
            data += packet

        if not data:
            break

        nparr = np.frombuffer(data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        cv2.imshow('Remote Screen', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    client_socket.close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
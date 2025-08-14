import socket
import pickle
import struct
import cv2
from pynput import mouse, keyboard

HOST = 'IP_СЕРВЕРА'
PORT = 5555

login = input("Введите логин: ")
password = input("Введите пароль: ")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.send(f"{login}:{password}".encode())
response = s.recv(1024)
if response != b"OK":
    print("Неверный логин или пароль")
    s.close()
    exit()

def send_command(cmd):
    data = pickle.dumps(cmd)
    s.sendall(struct.pack("Q", len(data)) + data)

def on_move(x, y):
    send_command({'type':'mouse_move','x':x,'y':y})

def on_click(x, y, button, pressed):
    if pressed:
        send_command({'type':'mouse_click','button':button})

def on_press(key):
    try:
        send_command({'type':'keyboard','key':key.char})
    except AttributeError:
        send_command({'type':'keyboard','key':key})

mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click)
keyboard_listener = keyboard.Listener(on_press=on_press)
mouse_listener.start()
keyboard_listener.start()

while True:
    packed_msg_size = s.recv(8)
    if not packed_msg_size:
        break
    msg_size = struct.unpack("Q", packed_msg_size)[0]
    data = b""
    while len(data) < msg_size:
        packet = s.recv(msg_size - len(data))
        if not packet:
            break
        data += packet
    frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    cv2.imshow("Admin Panel", frame)
    if cv2.waitKey(1) == ord('q'):
        break

cv2.destroyAllWindows()
s.close()
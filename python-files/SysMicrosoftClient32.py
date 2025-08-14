import socket
import base64
from io import BytesIO
from PIL import Image, ImageTk
import tkinter as tk
import threading
import pyautogui
import json

# Настройки
SERVER_IP = "192.168.1.100"  # Замени на IP сервера
PORT = 9999
WINDOW_SIZE = (1280, 720)  # Размер окна клиента

class ClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Screen Control")
        self.canvas = tk.Canvas(root, width=WINDOW_SIZE[0], height=WINDOW_SIZE[1])
        self.canvas.pack()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((SERVER_IP, PORT))
        print(f"Подключился к {SERVER_IP}:{PORT}")
        
        # Для хранения изображения
        self.photo = None
        
        # Обработчики событий
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Button-1>", self.on_mouse_click)
        self.root.bind("<Key>", self.on_key_press)
        
        # Запуск получения экрана
        threading.Thread(target=self.receive_screen, daemon=True).start()
    
    def on_mouse_move(self, event):
        # Масштабируем координаты
        x = event.x * (1920 / WINDOW_SIZE[0])  # Подстрой под разрешение сервера
        y = event.y * (1080 / WINDOW_SIZE[1])
        cmd = json.dumps({'type': 'mouse_move', 'x': x, 'y': y})
        self.client.sendall(cmd.encode('utf-8'))
    
    def on_mouse_click(self, event):
        cmd = json.dumps({'type': 'mouse_click'})
        self.client.sendall(cmd.encode('utf-8'))
    
    def on_key_press(self, event):
        cmd = json.dumps({'type': 'key_press', 'key': event.keysym})
        self.client.sendall(cmd.encode('utf-8'))
    
    def receive_screen(self):
        while True:
            try:
                data = self.client.recv(1024*1024).decode('utf-8')
                if data.startswith("SCREEN:"):
                    img_data = base64.b64decode(data[7:])
                    img = Image.open(BytesIO(img_data))
                    img = img.resize(WINDOW_SIZE, Image.Resampling.LANCZOS)
                    self.photo = ImageTk.PhotoImage(img)
                    self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
            except:
                break

if __name__ == "__main__":
    root = tk.Tk()
    app = ClientApp(root)
    root.mainloop()
import tkinter as tk
import socket
import ctypes

def send_udp_message():
    message = "LAMP ON"
   
    server_address = ('192.168.100.54', 49955)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(message.encode(), server_address)
        print(f"Wysłano wiadomość: {message}")
    finally:
        sock.close()
def send_udp_message1():
    message = "LAMP OFF"
    
    server_address = ('192.168.100.54', 49955)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(message.encode(), server_address)
        print(f"Wysłano wiadomość: {message}")
    finally:
        sock.close()       

# Tworzenie głównego okna aplikacji
root = tk.Tk()
root.title("UDP Sender")

# Tworzenie przycisku
send_button = tk.Button(root, text="LAMPY ON", command=send_udp_message)
send_button.pack(pady=20)
send_button1 = tk.Button(root, text="LAMPY OFF", command=send_udp_message1)
send_button1.pack(pady=20)
ctypes.windll.user32.ShowWindow( ctypes.windll.kernel32.GetConsoleWindow(), 6 )
# Uruchomienie głównej pętli zdarzeń
root.mainloop()

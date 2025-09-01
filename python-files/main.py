import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox

# --- Параметри підключення ---
HOST, PORT = 'localhost', 12345

# --- Клієнт ---
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# --- Головне вікно ---
root = tk.Tk()
root.title("Чат-клієнт")
root.geometry("500x500")

# Запит імені користувача
name = simpledialog.askstring("Авторизація", "Введіть ваше ім'я (нік):", parent=root)
if not name:
    messagebox.showerror("Помилка", "Ім'я обов'язкове!")
    root.destroy()
    exit(0)

client_socket.send(name.encode())

# --- Віджет для повідомлень ---
chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state="disabled", font=("Arial", 12))
chat_area.pack(padx=10, pady=10, fill="both", expand=True)

# --- Поле вводу ---
entry_message = tk.Entry(root, font=("Arial", 12))
entry_message.pack(padx=10, pady=5, fill="x")

def send_message():
    message = entry_message.get().strip()
    if message:
        try:
            client_socket.send(message.encode())
        except:
            pass
        if message.lower() in ("/quit", "exit"):
            try:
                client_socket.close()
            except:
                pass
            root.quit()
    entry_message.delete(0, tk.END)

def receive_messages():
    while True:
        try:
            response = client_socket.recv(1024).decode().strip()
            if response:
                chat_area.config(state="normal")
                chat_area.insert(tk.END, response + "\n")
                chat_area.yview(tk.END)  # автоскрол
                chat_area.config(state="disabled")
        except:
            break

# --- Кнопка відправки ---
send_button = tk.Button(root, text="Відправити", command=send_message)
send_button.pack(pady=5)

# Прив’язка Enter
entry_message.bind("<Return>", lambda event: send_message())

# --- Потік для прийому ---
threading.Thread(target=receive_messages, daemon=True).start()

# --- Закриття програми ---
def on_close():
    try:
        client_socket.send("/quit".encode())
        client_socket.close()
    except:
        pass
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

# --- Запуск ---
root.mainloop()

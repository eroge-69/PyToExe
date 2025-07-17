import tkinter as tk
from tkinter import messagebox

def open_profile():
    messagebox.showinfo("Profile", "Opening profile settings...")

def open_settings():
    messagebox.showinfo("Settings", "Opening settings...")

def send_message():
    message = entry.get()
    if message:
        chat_box.insert(tk.END, f"You: {message}\n")
        entry.delete(0, tk.END)

# Создание основного окна
root = tk.Tk()
root.title("Telegram Clone")

# Создание левого меню
left_frame = tk.Frame(root, width=200, bg='lightgrey')
left_frame.pack(side=tk.LEFT, fill=tk.Y)

profile_button = tk.Button(left_frame, text="Profile", command=open_profile)
profile_button.pack(pady=10, padx=10)

settings_button = tk.Button(left_frame, text="Settings", command=open_settings)
settings_button.pack(pady=10, padx=10)

# Создание основного чата
chat_frame = tk.Frame(root)
chat_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

chat_box = tk.Text(chat_frame, state=tk.NORMAL)
chat_box.pack(fill=tk.BOTH, expand=True)

entry_frame = tk.Frame(chat_frame)
entry_frame.pack(fill=tk.X)

entry = tk.Entry(entry_frame)
entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

send_button = tk.Button(entry_frame, text="Send", command=send_message)
send_button.pack(side=tk.RIGHT)

# Запуск основного цикла
root.mainloop()

import tkinter as tk
from tkinter import messagebox
import pyautogui
import time
import threading

def type_text(text, delay):
    time.sleep(delay)
    pyautogui.write(text, interval=0.05)

def start_typing():
    text = input_text.get("1.0", tk.END).strip()
    delay = int(delay_entry.get())

    if not text:
        messagebox.showwarning("Warning", "Please paste some text.")
        return

    threading.Thread(target=type_text, args=(text, delay)).start()
    messagebox.showinfo("Info", f"Typing will start in {delay} seconds.\nPlace your cursor in the input field or webpage.")

app = tk.Tk()
app.title("Auto Typer Tool")
app.geometry("400x300")

tk.Label(app, text="Paste your text below:").pack()
input_text = tk.Text(app, height=10, wrap='word')
input_text.pack(padx=10, pady=5)

tk.Label(app, text="Delay before typing (seconds):").pack()
delay_entry = tk.Entry(app)
delay_entry.insert(0, "5")
delay_entry.pack()

tk.Button(app, text="Start Typing", command=start_typing).pack(pady=10)

app.mainloop()


import tkinter as tk
from tkinter import messagebox
import subprocess
import socket
import psutil

def run_ping():
    try:
        output = subprocess.check_output(["ping", "-n", "4", "google.com"], universal_newlines=True)
    except subprocess.CalledProcessError as e:
        output = e.output
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, "=== PING google.com ===\n" + output)

def get_ip():
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        result_text.insert(tk.END, f"\n=== Локално IP ===\n{local_ip}\n")
    except:
        result_text.insert(tk.END, "\nНеуспешно извличане на IP адрес.\n")

def list_adapters():
    result_text.insert(tk.END, "\n=== Мрежови адаптери ===\n")
    adapters = psutil.net_if_stats()
    for adapter, stats in adapters.items():
        status = "Активен" if stats.isup else "Неактивен"
        result_text.insert(tk.END, f"{adapter}: {status}\n")

def copy_result():
    try:
        app.clipboard_clear()
        app.clipboard_append(result_text.get(1.0, tk.END))
        messagebox.showinfo("Копирано", "Резултатът е копиран в клипборда.")
    except:
        messagebox.showerror("Грешка", "Неуспешно копиране.")

app = tk.Tk()
app.title("kbrod.net")
app.geometry("500x400")

frame = tk.Frame(app)
frame.pack(pady=10)

ping_btn = tk.Button(frame, text="PING", width=10, command=run_ping)
ping_btn.grid(row=0, column=0, padx=5)

ip_btn = tk.Button(frame, text="Покажи IP", width=12, command=get_ip)
ip_btn.grid(row=0, column=1, padx=5)

adapters_btn = tk.Button(frame, text="Адаптери", width=12, command=list_adapters)
adapters_btn.grid(row=0, column=2, padx=5)

copy_btn = tk.Button(frame, text="Копирай", width=10, command=copy_result)
copy_btn.grid(row=0, column=3, padx=5)

result_text = tk.Text(app, height=20, width=60)
result_text.pack(padx=10, pady=10)

app.mainloop()

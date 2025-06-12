
import tkinter as tk
from tkinter import messagebox
import threading
import time

running_flags = [False for _ in range(8)]
threads = [None for _ in range(8)]

def simulate_attack(player_name, index, log_text):
    while running_flags[index]:
        log_text.insert(tk.END, f"[{player_name}] جارٍ إرسال SYN...
")
        log_text.see(tk.END)
        time.sleep(1)
    log_text.insert(tk.END, f"[{player_name}] تم إيقاف المحاكاة.
")

def start_simulation(entry, index, log_text):
    player_name = entry.get().strip()
    if not player_name:
        messagebox.showwarning("تحذير", "يرجى إدخال اسم اللاعب أولًا.")
        return

    if not running_flags[index]:
        running_flags[index] = True
        threads[index] = threading.Thread(target=simulate_attack, args=(player_name, index, log_text))
        threads[index].start()

def stop_simulation(index):
    running_flags[index] = False

def launch_gui():
    root = tk.Tk()
    root.title("محاكاة هجوم SYN - مشروع تخرج")
    root.geometry("700x600")
    root.resizable(False, False)

    entries = []
    for i in range(8):
        label = tk.Label(root, text=f"اللاعب {i+1}:", font=("Arial", 12))
        label.grid(row=i, column=0, padx=10, pady=5, sticky='e')

        entry = tk.Entry(root, width=30, font=("Arial", 12))
        entry.grid(row=i, column=1, padx=10, pady=5)
        entries.append(entry)

        start_button = tk.Button(root, text="ابدأ", width=10,
                                 command=lambda e=entry, idx=i: start_simulation(e, idx, log_area))
        start_button.grid(row=i, column=2, padx=5)

        stop_button = tk.Button(root, text="أوقف", width=10,
                                command=lambda idx=i: stop_simulation(idx))
        stop_button.grid(row=i, column=3, padx=5)

    log_area = tk.Text(root, height=15, width=80, font=("Arial", 10))
    log_area.grid(row=9, column=0, columnspan=4, padx=10, pady=20)

    root.mainloop()

if __name__ == "__main__":
    launch_gui()

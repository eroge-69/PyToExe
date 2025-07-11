
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import threading
import time
import winsound

class TimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AYCE Timer - Mama Musi Kenten")

        self.rows = []

        headers = ["Nama Meja", "Waktu Mulai (HH:MM)", "Waktu Selesai", "Sisa Waktu", "Status", "Mulai", "Reset"]
        for idx, text in enumerate(headers):
            ttk.Label(root, text=text).grid(row=0, column=idx, padx=5, pady=5)

        self.add_button = ttk.Button(root, text="Tambah Meja", command=self.add_row)
        self.add_button.grid(row=1, column=0, pady=10)

        self.update_thread = threading.Thread(target=self.update_timers)
        self.update_thread.daemon = True
        self.update_thread.start()

    def add_row(self):
        row_index = len(self.rows) + 2
        meja_name_var = tk.StringVar()
        meja_name_entry = ttk.Entry(self.root, textvariable=meja_name_var)
        meja_name_entry.grid(row=row_index, column=0)

        start_time_var = tk.StringVar()
        start_entry = ttk.Entry(self.root, textvariable=start_time_var)
        start_entry.grid(row=row_index, column=1)

        end_label = ttk.Label(self.root, text="-")
        time_left_label = ttk.Label(self.root, text="Belum mulai")
        status_label = ttk.Label(self.root, text="-", foreground="black")

        start_btn = ttk.Button(self.root, text="Mulai")
        reset_btn = ttk.Button(self.root, text="Reset")

        end_label.grid(row=row_index, column=2)
        time_left_label.grid(row=row_index, column=3)
        status_label.grid(row=row_index, column=4)
        start_btn.grid(row=row_index, column=5)
        reset_btn.grid(row=row_index, column=6)

        row_data = {
            'meja_name_var': meja_name_var,
            'start_time_var': start_time_var,
            'end_label': end_label,
            'time_left_label': time_left_label,
            'status_label': status_label,
            'start_btn': start_btn,
            'reset_btn': reset_btn,
            'row_index': row_index,
            'end_time': None,
            'expired': False
        }

        start_btn.config(command=lambda: self.start_timer(row_data))
        reset_btn.config(command=lambda: self.reset_timer(row_data))

        self.rows.append(row_data)

    def start_timer(self, row):
        try:
            start_time_str = row['start_time_var'].get()
            start_time = datetime.strptime(start_time_str, "%H:%M")
            today = datetime.now().date()
            full_start_time = datetime.combine(today, start_time.time())
            end_time = full_start_time + timedelta(minutes=90)

            row['end_time'] = end_time
            row['end_label'].config(text=end_time.strftime("%H:%M:%S"))
            row['time_left_label'].config(text="90:00")
            row['status_label'].config(text="✅", foreground="green")
            row['expired'] = False
        except ValueError:
            messagebox.showerror("Format Salah", "Gunakan format jam HH:MM, contoh: 14:30")

    def reset_timer(self, row):
        row['start_time_var'].set("")
        row['end_time'] = None
        row['end_label'].config(text="-")
        row['time_left_label'].config(text="Belum mulai")
        row['status_label'].config(text="-", foreground="black")
        row['expired'] = False

    def update_timers(self):
        while True:
            now = datetime.now()
            for row in self.rows:
                if row['end_time']:
                    remaining = row['end_time'] - now
                    minutes, seconds = divmod(int(remaining.total_seconds()), 60)

                    if remaining.total_seconds() <= 0:
                        row['time_left_label'].config(text="00:00")
                        row['status_label'].config(text="⛔ HABIS", foreground="red")
                        if not row['expired']:
                            self.show_alert(row['meja_name_var'].get() or "Meja")
                            row['expired'] = True
                    elif remaining.total_seconds() < 600:
                        row['time_left_label'].config(text=f"{minutes:02d}:{seconds:02d}")
                        row['status_label'].config(text="⚠️ SEGERA", foreground="orange")
                    else:
                        row['time_left_label'].config(text=f"{minutes:02d}:{seconds:02d}")
                        row['status_label'].config(text="✅", foreground="green")
            time.sleep(1)

    def show_alert(self, meja_name):
        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        messagebox.showinfo("Waktu Habis", f"Waktu untuk {meja_name} sudah habis!")

if __name__ == "__main__":
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()

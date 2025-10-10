import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import threading
import time
import winsound  # voor geluid op Windows

def start_countdown(input_window, time_str):
    try:
        now = datetime.now()
        target_time = datetime.strptime(time_str, "%H:%M").replace(
            year=now.year, month=now.month, day=now.day
        )
        if target_time < now:
            target_time += timedelta(days=1)

        total_seconds = (target_time - now).total_seconds()

        # Sluit het invoervenster
        input_window.destroy()

        # Countdown popup
        root = tk.Tk()
        root.title("Countdown")
        root.geometry("350x200")
        root.resizable(False, False)
        root.configure(bg="#101020")

        title_label = tk.Label(
            root, text=f"Countdown tot {time_str}",
            font=("Segoe UI", 14, "bold"), fg="#00ffcc", bg="#101020"
        )
        title_label.pack(pady=20)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "TProgressbar",
            thickness=20,
            troughcolor="#202040",
            background="#00ffaa",
            bordercolor="#101020",
            relief="flat"
        )

        progress = ttk.Progressbar(
            root, orient="horizontal", length=280, mode="determinate", style="TProgressbar"
        )
        progress.pack(pady=15)

        percent_label = tk.Label(
            root, text="0%", font=("Segoe UI", 12), fg="#00ffaa", bg="#101020"
        )
        percent_label.pack()

        status_label = tk.Label(
            root, text="Wachten tot " + time_str, font=("Segoe UI", 10), fg="white", bg="#101020"
        )
        status_label.pack(pady=5)

        def update_progress():
            start_time = datetime.now()
            while datetime.now() < target_time:
                elapsed = (datetime.now() - start_time).total_seconds()
                progress_value = min(100, (elapsed / total_seconds) * 100)
                progress["value"] = progress_value
                percent_label.config(text=f"{progress_value:.1f}%")
                time.sleep(1)

            progress["value"] = 100
            percent_label.config(text="100%")
            status_label.config(text="🎉 Tijd bereikt!")
            title_label.config(text="Klaar!")
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            messagebox.showinfo("Klaar!", f"Het is nu {time_str}!")

        threading.Thread(target=update_progress, daemon=True).start()
        root.mainloop()

    except ValueError:
        messagebox.showerror("Fout", "Gebruik het formaat HH:MM (bijv. 16:00)")

# Invoervenster
input_window = tk.Tk()
input_window.title("Countdown Instellen")
input_window.geometry("300x150")
input_window.resizable(False, False)

tk.Label(input_window, text="Voer tijd in (HH:MM):", font=("Arial", 12)).pack(pady=10)
time_entry = tk.Entry(input_window, font=("Arial", 12), justify="center")
time_entry.pack()

tk.Button(
    input_window, 
    text="Start", 
    font=("Arial", 12), 
    command=lambda: start_countdown(input_window, time_entry.get())
).pack(pady=10)

input_window.mainloop()

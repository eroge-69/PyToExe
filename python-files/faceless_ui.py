import tkinter as tk
import threading
import random
import time
import pyperclip

MAX_LOG_LINES = 100
MAX_CLIPBOARD_LENGTH = 1500

class FacelessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Roblox - Faceless External Tool")
        self.root.geometry("600x400")
        self.root.configure(bg="black")
        self.logs = []

        self.title_label = tk.Label(root, text="FACELESS 🎭", fg="#39FF14", bg="black", font=("Consolas", 20, "bold"))
        self.title_label.pack(pady=10)

        self.log_box = tk.Text(root, height=15, width=70, bg="#111", fg="white", font=("Consolas", 10))
        self.log_box.pack()

        self.copy_button = tk.Button(root, text="📋 Copy Logs", command=self.copy_logs, bg="#444", fg="white")
        self.copy_button.pack(pady=5)

        self.animate_masks()

    def log(self, message):
        timestamp = time.strftime("[%H:%M:%S] ")
        full_message = timestamp + message
        self.logs.append(full_message)
        if len(self.logs) > MAX_LOG_LINES:
            self.logs.pop(0)
        self.update_log_box()

    def update_log_box(self):
        self.log_box.delete(1.0, tk.END)
        self.log_box.insert(tk.END, "\n".join(self.logs))

    def copy_logs(self):
        try:
            log_text = "\n".join(self.logs)
            clipped = log_text[:MAX_CLIPBOARD_LENGTH]
            pyperclip.copy(clipped)
            self.log("Copied logs to clipboard.")
        except Exception as e:
            self.log(f"Clipboard copy failed: {str(e)}")

    def animate_masks(self):
        def fall():
            while True:
                time.sleep(random.uniform(0.2, 0.6))
                emoji = "🎭"
                self.title_label.config(text=f"FACELESS {emoji}")
                time.sleep(0.05)
                self.title_label.config(text="FACELESS")
        thread = threading.Thread(target=fall, daemon=True)
        thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = FacelessApp(root)

    modules = [
        "Anti-VM bypass loaded.",
        "FPS Unlocker initialized.",
        "Silent Aim ready.",
        "ESP overlay attached.",
        "Clipboard logger active.",
        "Godmode toggle online.",
        "Teleport handler ready.",
        "Command bar listening..."
    ]
    for msg in modules:
        app.log(msg)
        time.sleep(0.2)

    root.mainloop()

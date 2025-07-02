import tkinter as tk
from pynput import mouse

MONITOR_3_X_START = 3200
MONITOR_3_X_END = 3840
MONITOR_3_Y_START = 0
MONITOR_3_Y_END = 1080

COUNT_FILE = "spin_count.txt"

class ClickCounterApp:
    def __init__(self, master):
        self.master = master
        self.count = 0
        self.running = False
        self.listener = None

        master.title("Spin Klickzähler Monitor 3 - Angepasst")

        self.label = tk.Label(master, text=f"Spins: {self.count}", font=("Arial", 20))
        self.label.pack(pady=10)

        self.start_button = tk.Button(master, text="Start", command=self.start)
        self.start_button.pack(fill="x")

        self.stop_button = tk.Button(master, text="Stop", command=self.stop)
        self.stop_button.pack(fill="x")

        self.reset_button = tk.Button(master, text="Reset", command=self.reset)
        self.reset_button.pack(fill="x")

        master.protocol("WM_DELETE_WINDOW", self.on_close)

    def start(self):
        if not self.running:
            self.running = True
            self.listener = mouse.Listener(on_click=self.on_click)
            self.listener.start()
            print("Listener gestartet. Klicke auf Monitor 3, um Spins zu zählen.")

    def stop(self):
        if self.running:
            self.running = False
            if self.listener:
                self.listener.stop()
                self.listener = None
            print("Listener gestoppt.")

    def reset(self):
        self.count = 0
        self.update_label()
        self.save_count()
        print("Zähler zurückgesetzt.")

    def update_label(self):
        self.label.config(text=f"Spins: {self.count}")

    def save_count(self):
        with open(COUNT_FILE, "w") as f:
            f.write(str(self.count))

    def on_click(self, x, y, button, pressed):
        if pressed and self.running:
            if MONITOR_3_X_START <= x <= MONITOR_3_X_END and MONITOR_3_Y_START <= y <= MONITOR_3_Y_END:
                self.count += 1
                self.update_label()
                self.save_count()
                print(f"Spin gezählt! Gesamt: {self.count}")
            else:
                print(f"Klick außerhalb des Bereichs: x={x}, y={y}")

    def on_close(self):
        self.stop()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ClickCounterApp(root)
    root.mainloop()

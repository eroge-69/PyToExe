import tkinter as tk
from datetime import datetime

class CounterApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Counting App")
        self.count = 0

        self.label = tk.Label(master, text=str(self.count), font=("Arial", 64), width=5)
        self.label.pack(pady=30)

        btn_frame = tk.Frame(master)
        btn_frame.pack()

        self.increment_btn = tk.Button(btn_frame, text="+", font=("Arial", 24), width=5, command=self.increment)
        self.increment_btn.grid(row=0, column=0, padx=15, pady=10)

        self.decrement_btn = tk.Button(btn_frame, text="-", font=("Arial", 24), width=5, command=self.decrement)
        self.decrement_btn.grid(row=0, column=1, padx=15, pady=10)

        self.clear_btn = tk.Button(master, text="Clear", font=("Arial", 18), width=12, command=self.clear)
        self.clear_btn.pack(pady=15)

        # Extra large, vibrant green time display
        self.time_label = tk.Label(master, font=("Arial", 36, "bold"), fg="#00FF00")
        self.time_label.pack(side="bottom", pady=15)
        self.update_time()

    def increment(self):
        self.count += 1
        self.update_label()

    def decrement(self):
        self.count -= 1
        self.update_label()

    def clear(self):
        self.count = 0
        self.update_label()

    def update_label(self):
        self.label.config(text=str(self.count))

    def update_time(self):
        now = datetime.now().strftime("%H:%M:%S")
        self.time_label.config(text=now)
        self.master.after(1000, self.update_time)  # update every second

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("350x450")  # Larger window
    app = CounterApp(root)
    root.mainloop()

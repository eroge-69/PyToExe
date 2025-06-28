
import tkinter as tk
from tkinter import messagebox, simpledialog
import time
import threading

class Client:
    def __init__(self, number, frame, row):
        self.number = number
        self.time_left = 0
        self.running = False

        self.label = tk.Label(frame, text=f"Client {number}", font=('Arial', 12, 'bold'))
        self.label.grid(row=row, column=0, padx=5, pady=5)

        self.time_display = tk.Label(frame, text="00:00:00", font=('Arial', 12), width=10)
        self.time_display.grid(row=row, column=1, padx=5, pady=5)

        self.start_btn = tk.Button(frame, text="▶", command=self.start_timer, width=3)
        self.start_btn.grid(row=row, column=2)

        self.pause_btn = tk.Button(frame, text="⏸", command=self.pause_timer, width=3)
        self.pause_btn.grid(row=row, column=3)

        self.stop_btn = tk.Button(frame, text="⛔", command=self.stop_timer, width=3)
        self.stop_btn.grid(row=row, column=4)

        self.buy_btn = tk.Button(frame, text="💰", command=self.buy_time, width=3)
        self.buy_btn.grid(row=row, column=5)

    def update_display(self):
        hrs, rem = divmod(self.time_left, 3600)
        mins, secs = divmod(rem, 60)
        self.time_display.config(text=f"{int(hrs):02}:{int(mins):02}:{int(secs):02}")

    def timer_loop(self):
        while self.running and self.time_left > 0:
            time.sleep(1)
            self.time_left -= 1
            self.update_display()
        if self.time_left <= 0 and self.running:
            self.running = False
            messagebox.showinfo("Fotoana tapitra", f"Tapitra ny ora an'ny Client {self.number}")

    def start_timer(self):
        if self.time_left > 0 and not self.running:
            self.running = True
            threading.Thread(target=self.timer_loop, daemon=True).start()

    def pause_timer(self):
        self.running = False

    def stop_timer(self):
        self.running = False
        self.time_left = 0
        self.update_display()

    def buy_time(self):
        try:
            amount = simpledialog.askinteger("Mividy ora", f"Vola naloan'i Client {self.number} (Ar)?")
            if amount:
                minutes = (amount // 100) * 20  # 100 Ar = 20 mn
                self.time_left += minutes * 60
                self.update_display()
        except:
            messagebox.showerror("Hadisoana", "Diso ny sandan'ny vola!")

def main_app():
    root = tk.Tk()
    root.title("CyberChrono - FinishTime Lite Malagasy Edition")
    root.geometry("600x800")
    frame = tk.Frame(root)
    frame.pack(pady=10)

    clients = []
    for i in range(20):
        client = Client(i + 1, frame, i)
        clients.append(client)

    root.mainloop()

if __name__ == "__main__":
    main_app()

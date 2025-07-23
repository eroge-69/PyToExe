import tkinter as tk
import time

class TimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Timp = Bani")
        self.root.geometry("300x200")
        self.root.attributes('-topmost', True)  # always on top

        self.running = False
        self.start_time = None
        self.elapsed_time = 0

        self.time_label = tk.Label(root, text="00:00", font=("Helvetica", 40))
        self.time_label.pack(pady=10)

        self.euro_label = tk.Label(root, text="0 €", font=("Helvetica", 20))
        self.euro_label.pack(pady=5)

        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        self.start_button = tk.Button(button_frame, text="Start", command=self.start)
        self.start_button.grid(row=0, column=0, padx=5)

        self.stop_button = tk.Button(button_frame, text="Stop", command=self.stop)
        self.stop_button.grid(row=0, column=1, padx=5)

        self.reset_button = tk.Button(button_frame, text="Reset", command=self.reset)
        self.reset_button.grid(row=0, column=2, padx=5)

        self.update_timer()

    def update_timer(self):
        if self.running:
            current_time = time.time()
            self.elapsed_time = current_time - self.start_time
        minutes = int(self.elapsed_time // 60)
        seconds = int(self.elapsed_time % 60)
        self.time_label.config(text=f"{minutes:02}:{seconds:02}")
        self.euro_label.config(text=f"{minutes} €")
        self.root.after(500, self.update_timer)

    def start(self):
        if not self.running:
            self.start_time = time.time() - self.elapsed_time
            self.running = True

    def stop(self):
        if self.running:
            self.running = False
            self.elapsed_time = time.time() - self.start_time

    def reset(self):
        self.running = False
        self.elapsed_time = 0
        self.time_label.config(text="00:00")
        self.euro_label.config(text="0 €")

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()

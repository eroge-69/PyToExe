import tkinter as tk

class EmailSimulator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Symulacja Kont Email (Automatyczna)")
        self.geometry("800x600")
        self.panels = []
        self.colors = ['#a8e6cf', '#dcedc1', '#aed581', '#7cb342']
        self.message = ""
        self.current_idx = 0
        self.running = False

        self.setup_ui()

    def setup_ui(self):
        for i in range(4):
            frame = tk.Frame(self, bg=self.colors[i], width=400, height=300, highlightbackground="black", highlightthickness=1)
            frame.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="nsew")

            label = tk.Label(frame, text=f"Konto {i+1}", bg=self.colors[i], font=("Arial", 14, "bold"))
            label.pack(pady=10)

            text = tk.Text(frame, height=6, width=40)
            text.pack()

            self.panels.append((text, frame))

        self.start_btn = tk.Button(self, text="Start automatycznego obiegu", command=self.start_cycle)
        self.start_btn.grid(row=2, column=0, columnspan=2, pady=10)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def start_cycle(self):
        if not self.running:
            self.message = self.panels[0][0].get("1.0", tk.END).strip()
            self.panels[0][0].delete("1.0", tk.END)
            self.running = True
            self.cycle_message()

    def cycle_message(self):
        if not self.running or not self.message:
            return

        next_idx = (self.current_idx + 1) % 4
        text_widget, _ = self.panels[next_idx]
        text_widget.insert(tk.END, f"Otrzymano od Konto {self.current_idx + 1}: {self.message}\n")
        self.current_idx = next_idx

        if self.current_idx == 0:
            self.running = False
            return

        self.after(5000, self.cycle_message)  # 5 sekund

if __name__ == "__main__":
    app = EmailSimulator()
    app.mainloop()

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import time

# czas odliczania w sekundach (np. 30 min = 1800s)
COUNTDOWN_TIME = 1800  

class MetinTimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tabela Metinów - Śmierci")

        # Wczytanie tła (upewnij się, że plik 9ogonow.png jest w tym samym folderze!)
        try:
            bg_image = Image.open("9ogonow.png")
            bg_image = bg_image.resize((900, 500), Image.ANTIALIAS)
            self.bg = ImageTk.PhotoImage(bg_image)

            background_label = tk.Label(root, image=self.bg)
            background_label.place(relwidth=1, relheight=1)
        except:
            root.configure(bg="black")

        # Style
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 10, "bold"))
        style.map("TButton",
                  background=[("active", "gold")],
                  foreground=[("active", "black")])

        self.channels = ["CH1","CH2","CH3","CH4","CH5","CH6","CH7"]
        self.sections = ["Śmierci Dół", "Śmierci Środek", "Śmierci Las"]

        self.timers = {}
        self.labels = {}

        self.build_ui()

    def build_ui(self):
        # Nagłówki
        header = tk.Label(self.root, text="Tabela Metinów", font=("Arial", 16, "bold"),
                          bg="black", fg="gold")
        header.grid(row=0, column=0, columnspan=len(self.sections)+1, pady=10)

        for j, sec in enumerate(self.sections):
            lbl = tk.Label(self.root, text=sec, font=("Arial", 12, "bold"),
                           bg="darkred", fg="white", padx=10, pady=5, relief="ridge")
            lbl.grid(row=1, column=j+1, sticky="nsew")

        # Tabela kanałów
        for i, ch in enumerate(self.channels):
            tk.Label(self.root, text=ch, font=("Arial", 11, "bold"),
                     bg="gray20", fg="white", padx=5, pady=5).grid(row=i+2, column=0, sticky="nsew")

            for j, sec in enumerate(self.sections):
                key = (ch, sec)
                self.timers[key] = None

                # przycisk Zbij
                btn_zbij = tk.Button(self.root, text="Zbij", bg="gold", fg="black",
                                     command=lambda c=ch, s=sec: self.start_timer(c, s))
                btn_zbij.grid(row=i+2, column=j+1, sticky="nsew")

                # label z czasem
                lbl_time = tk.Label(self.root, text="--:--", bg="black", fg="white",
                                    font=("Consolas", 11))
                lbl_time.grid(row=i+2, column=j+1, padx=60, sticky="e")
                self.labels[key] = lbl_time

                # przycisk Reset
                btn_reset = tk.Button(self.root, text="Reset", bg="red", fg="white",
                                      command=lambda c=ch, s=sec: self.reset_timer(c, s))
                btn_reset.grid(row=i+2, column=j+1, padx=5, sticky="w")

    def start_timer(self, ch, sec):
        key = (ch, sec)
        end_time = time.time() + COUNTDOWN_TIME
        self.timers[key] = end_time
        self.update_timer(ch, sec)

    def reset_timer(self, ch, sec):
        key = (ch, sec)
        self.timers[key] = None
        self.labels[key].config(text="--:--")

    def update_timer(self, ch, sec):
        key = (ch, sec)
        if self.timers[key] is not None:
            remaining = int(self.timers[key] - time.time())
            if remaining > 0:
                mins, secs = divmod(remaining, 60)
                self.labels[key].config(text=f"{mins:02}:{secs:02}")
                self.root.after(1000, self.update_timer, ch, sec)
            else:
                self.labels[key].config(text="00:00")
                self.timers[key] = None

if __name__ == "__main__":
    root = tk.Tk()
    app = MetinTimerApp(root)
    root.mainloop()


import tkinter as tk
from tkinter import messagebox

class SlotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Slot Strateji Takip Aracı")
        self.root.geometry("400x400")

        self.slots = ["Sugar Rush", "Big Bass", "Wanted DOAW", "Book of Dead", "Zeus vs Hades"]

        tk.Label(root, text="Slot Seçin:").pack(pady=5)
        self.slot_var = tk.StringVar(value=self.slots[0])
        tk.OptionMenu(root, self.slot_var, *self.slots).pack(pady=5)

        tk.Label(root, text="Bet 1 (10 TL) Kazanç:").pack()
        self.bet1 = tk.Entry(root)
        self.bet1.pack()

        tk.Label(root, text="Bet 2 (20 TL) Kazanç:").pack()
        self.bet2 = tk.Entry(root)
        self.bet2.pack()

        tk.Label(root, text="Bet 3 (40 TL) Kazanç:").pack()
        self.bet3 = tk.Entry(root)
        self.bet3.pack()

        tk.Button(root, text="Analiz Et", command=self.analyze).pack(pady=10)

        self.result = tk.Label(root, text="")
        self.result.pack()

    def analyze(self):
        try:
            b1 = float(self.bet1.get())
            b2 = float(self.bet2.get())
            b3 = float(self.bet3.get())
            total = b1 + b2 + b3

            if b3 >= 80 or b2 >= 40:
                decision = "Yüksek kazanç. Slotu bırak, kârı yedekle."
            elif b1 == 0 and b2 == 0 and b3 == 0:
                decision = "Hiç kazanç yok. Slotu değiştir."
            elif total >= 60:
                decision = "Orta düzey kazanç. Slotta 10 spin daha oynanabilir."
            else:
                decision = "Kazanç düşük. Yeni slota geç."

            self.result.config(text=f"Sonuç: {decision}\nToplam Kazanç: {total:.2f} TL")
        except ValueError:
            messagebox.showerror("Hata", "Lütfen tüm kazanç alanlarını sayısal girin.")


if __name__ == '__main__':
    root = tk.Tk()
    app = SlotApp(root)
    root.mainloop()

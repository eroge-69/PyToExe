import tkinter as tk
from tkinter import messagebox
from random import randint
import time

class FlowerTycoon:
    def __init__(self, root):
        self.root = root
        self.root.title("Цветочный бизнес бабушки")
        self.root.geometry("800x600")
        self.root.configure(bg="lightyellow")

        # Игровые переменные
        self.balance = 5
        self.flowers = {"Ромашка": 0, "Тюльпан": 0}
        self.goal = 1000
        self.game_over = False
        self.sornyaki = []  # список (ID, x, y)

        self.flower_data = {
            "Ромашка": {"price": 5, "income": 1, "emoji": "🌼"},
            "Тюльпан": {"price": 15, "income": 20, "emoji": "🌷"}
        }

        # Интерфейс
        self.label_balance = tk.Label(root, text=f"Баланс: {self.balance} монет", font=("Arial", 16), bg="lightyellow")
        self.label_balance.pack(pady=10)

        self.label_flowers = tk.Label(root, text=self.get_flower_text(), font=("Arial", 14), bg="lightyellow")
        self.label_flowers.pack()

        self.shop_frame = tk.Frame(root, bg="lightyellow")
        self.shop_frame.pack(pady=10)

        self.button_daisy = tk.Button(self.shop_frame, text="Купить Ромашку 🌼 (5 монет)", font=("Arial", 12),
                                      command=lambda: self.buy_flower("Ромашка"))
        self.button_daisy.grid(row=0, column=0, padx=10)

        self.button_tulip = tk.Button(self.shop_frame, text="Купить Тюльпан 🌷 (15 монет)", font=("Arial", 12),
                                      command=lambda: self.buy_flower("Тюльпан"))
        self.button_tulip.grid(row=0, column=1, padx=10)

        self.garden = tk.Canvas(root, width=750, height=400, bg="lightgreen", relief="sunken", bd=3)
        self.garden.pack(pady=10)
        self.garden.bind("<Button-1>", self.handle_click)

        self.update_income()
        self.spawn_sornyak()

    def get_flower_text(self):
        return f"Ромашек: {self.flowers['Ромашка']} | Тюльпанов: {self.flowers['Тюльпан']}"

    def buy_flower(self, flower_type):
        if self.game_over:
            return
        price = self.flower_data[flower_type]["price"]
        if self.balance >= price:
            self.balance -= price
            self.flowers[flower_type] += 1
            self.label_balance.config(text=f"Баланс: {self.balance} монет")
            self.label_flowers.config(text=self.get_flower_text())
            self.add_flower_to_garden(flower_type)
        else:
            messagebox.showwarning("Недостаточно монет", f"У вас не хватает монет на {flower_type.lower()}.")

    def add_flower_to_garden(self, flower_type):
        x = randint(20, 700)
        y = randint(20, 350)
        emoji = self.flower_data[flower_type]["emoji"]
        self.garden.create_text(x, y, text=emoji, font=("Arial", 20))

    def update_income(self):
        if not self.game_over:
            income = 0
            for flower, count in self.flowers.items():
                income += count * self.flower_data[flower]["income"]
            self.balance += income
            self.label_balance.config(text=f"Баланс: {self.balance} монет")

            if self.balance >= self.goal:
                self.win_game()
        self.root.after(1000, self.update_income)

    def spawn_sornyak(self):
        if self.game_over:
            return
        x = randint(30, 700)
        y = randint(30, 350)
        weed_id = self.garden.create_text(x, y, text="🌿", font=("Arial", 18), fill="darkgreen")
        self.sornyaki.append({"id": weed_id, "x": x, "y": y})
        self.root.after(8000, lambda: self.check_sornyak(weed_id))
        self.root.after(randint(5000, 8000), self.spawn_sornyak)

    def check_sornyak(self, weed_id):
        if self.game_over:
            return
        for weed in self.sornyaki:
            if weed["id"] == weed_id:
                self.balance -= 10
                if self.balance < 0:
                    self.balance = 0
                self.label_balance.config(text=f"Баланс: {self.balance} монет")
                self.garden.delete(weed_id)
                self.sornyaki.remove(weed)
                break

    def handle_click(self, event):
        if self.game_over:
            return
        clicked_items = self.garden.find_overlapping(event.x, event.y, event.x + 1, event.y + 1)
        for item in clicked_items:
            for weed in self.sornyaki:
                if weed["id"] == item:
                    self.garden.delete(item)
                    self.sornyaki.remove(weed)
                    return

    def win_game(self):
        self.game_over = True
        self.button_daisy.config(state="disabled")
        self.button_tulip.config(state="disabled")
        messagebox.showinfo("Победа!", "ПОЗДРАВЛЯЕМ С ДНЕМ РОЖДЕНИЯ!")

if __name__ == "__main__":
    root = tk.Tk()
    app = FlowerTycoon(root)
    root.mainloop()

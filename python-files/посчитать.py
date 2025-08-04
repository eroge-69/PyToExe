import tkinter as tk
from tkinter import ttk, messagebox

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Калькулятор процентов")

        # --- Предопределённая база товаров (название: цена) ---
        self.product_db = {
            "Псевдыч":100000,
"Бюрер":39000,
"Химера":50000,
"Контролер":46500,
"Кровосос":9000,
"Излом":6300,
"Слепой пес":2700,
"Псведособака":4900,
"Кабан":2700,
"Снорк":4200,
"Зомби":3000,
"Плоть":2400,
"Тушкан":2100,
"Кот":3600
        }

        self.cart = []

        # --- UI: Выбор товара ---
        tk.Label(root, text="Товар:").grid(row=0, column=0)
        self.product_var = tk.StringVar()
        self.product_box = ttk.Combobox(root, textvariable=self.product_var, values=list(self.product_db.keys()))
        self.product_box.grid(row=0, column=1)

        # --- Количество ---
        tk.Label(root, text="Количество:").grid(row=0, column=2)
        self.quantity_entry = tk.Entry(root, width=5)
        self.quantity_entry.grid(row=0, column=3)

        # --- Кнопка добавления ---
        tk.Button(root, text="Добавить", command=self.add_item).grid(row=0, column=4, padx=10)

        # --- Процент ---
        tk.Label(root, text="Процент (забрать):").grid(row=1, column=0)
        self.percent_entry = tk.Entry(root)
        self.percent_entry.grid(row=1, column=1)

        # --- Кнопка расчёта ---
        tk.Button(root, text="Рассчитать", command=self.calculate).grid(row=1, column=2, columnspan=2)

        # --- Список выбранных позиций ---
        self.item_listbox = tk.Listbox(root, width=70)
        self.item_listbox.grid(row=2, column=0, columnspan=5, pady=10)

        # --- Результат ---
        self.result_label = tk.Label(root, text="", fg="blue", font=("Arial", 12))
        self.result_label.grid(row=3, column=0, columnspan=5)

    def add_item(self):
        name = self.product_var.get()
        quantity = self.quantity_entry.get()

        if not name or name not in self.product_db:
            messagebox.showwarning("Ошибка", "Выберите товар из списка.")
            return
        if not quantity.isdigit() or int(quantity) <= 0:
            messagebox.showwarning("Ошибка", "Введите корректное количество.")
            return

        price = self.product_db[name]
        quantity = int(quantity)
        total = price * quantity

        self.cart.append((name, price, quantity, total))
        self.item_listbox.insert(tk.END, f"{name} — {price}₽ x {quantity} = {total:.2f}₽")
        self.quantity_entry.delete(0, tk.END)

    def calculate(self):
        if not self.cart:
            messagebox.showinfo("Пусто", "Добавьте хотя бы одну позицию.")
            return
        try:
            percent = float(self.percent_entry.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректный процент.")
            return

        total_sum = sum(item[3] for item in self.cart)
        you_take = total_sum * (percent / 100)
        to_return = total_sum - you_take

        self.result_label.config(
            text=f"Итого: {total_sum:.2f}₽\nВы забираете: {you_take:.2f}₽\nОтдаёте: {to_return:.2f}₽"
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()

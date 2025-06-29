import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import math
import csv

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Лабораторная работа №5 - Вариант 9")
        self.geometry("600x400")

        self.create_menu()

    def create_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        task_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Задачи", menu=task_menu)
        task_menu.add_command(label="Треугольник", command=self.show_triangle_frame)
        task_menu.add_command(label="Файл с рождаемостью", command=self.show_table_frame)

        menubar.add_command(label="Об авторе", command=self.show_author)

    def show_author(self):
        messagebox.showinfo("Об авторе", "Программа создана студентом по варианту №9\nЛабораторные 1 и 3 на Python GUI")

    def show_triangle_frame(self):
        self.clear_frame()
        frame = tk.Frame(self)
        frame.pack(pady=20)

        tk.Label(frame, text="Катет a:").grid(row=0, column=0)
        a_entry = tk.Entry(frame)
        a_entry.grid(row=0, column=1)

        tk.Label(frame, text="Катет b:").grid(row=1, column=0)
        b_entry = tk.Entry(frame)
        b_entry.grid(row=1, column=1)

        result_label = tk.Label(frame, text="")
        result_label.grid(row=3, column=0, columnspan=2)

        def calc():
            try:
                a = float(a_entry.get())
                b = float(b_entry.get())
                c = math.hypot(a, b)
                perimeter = a + b + c
                area = 0.5 * a * b
                result_label.config(text=f"Периметр: {perimeter:.2f}, Площадь: {area:.2f}")
            except ValueError:
                messagebox.showerror("Ошибка", "Вводите только числа.")

        tk.Button(frame, text="Посчитать", command=calc).grid(row=2, column=0, columnspan=2)

    def show_table_frame(self):
        self.clear_frame()
        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(frame, columns=("age", "city", "village"), show="headings")
        for col in ("age", "city", "village"):
            self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True)

        button_frame = tk.Frame(self)
        button_frame.pack()

        def load_file():
            file_path = filedialog.askopenfilename(filetypes=[("TSV files", "*.tsv")])
            if not file_path:
                return
            self.data = []
            self.tree.delete(*self.tree.get_children())
            with open(file_path, encoding="utf-8") as f:
                reader = csv.reader(f, delimiter="\t")
                for row in reader:
                    self.data.append(row)
                    self.tree.insert("", "end", values=row)

        def solve():
            try:
                k = float(simpledialog.askstring("Ввод K", "Введите K:"))
                filtered = [row for row in self.data if float(row[1].replace(",", ".")) <= k]
                self.tree.delete(*self.tree.get_children())
                for row in filtered:
                    self.tree.insert("", "end", values=row)
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        def save_file():
            file_path = filedialog.asksaveasfilename(defaultextension=".csv")
            if not file_path:
                return
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                for row_id in self.tree.get_children():
                    writer.writerow(self.tree.item(row_id)["values"])
            messagebox.showinfo("Сохранено", f"Файл сохранён: {file_path}")

        tk.Button(button_frame, text="Открыть файл", command=load_file).pack(side="left", padx=5)
        tk.Button(button_frame, text="Решить", command=solve).pack(side="left", padx=5)
        tk.Button(button_frame, text="Сохранить", command=save_file).pack(side="left", padx=5)

    def clear_frame(self):
        for widget in self.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()

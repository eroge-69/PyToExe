import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import json
from datetime import datetime

class SmokeCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("GTA 5 RP Калькулятор перекуров v3.0")
        self.root.geometry("950x700")
        self.root.resizable(True, True)
        
        # Настройка стилей
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        self.style.configure("TButton", font=("Arial", 10), padding=5)
        
        # Данные приложения
        self.products = []
        self.current_image = None
        self.selected_product_index = None
        self.load_data()
        
        # Создание интерфейса
        self.create_widgets()
        
    def create_widgets(self):
        # Основные фреймы
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Фрейм для ввода данных (левый верхний)
        input_frame = ttk.LabelFrame(main_frame, text="Данные о сделке", padding=10)
        input_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Фрейм для просмотра фото (правый верхний)
        self.preview_frame = ttk.LabelFrame(main_frame, text="Просмотр товара", padding=10)
        self.preview_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # Фрейм истории (нижняя часть)
        history_frame = ttk.LabelFrame(main_frame, text="История сделок", padding=10)
        history_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        
        # Настройка веса строк и столбцов
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=3)
        main_frame.grid_columnconfigure(0, weight=2)
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Поля ввода
        ttk.Label(input_frame, text="Название товара:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.name_entry = ttk.Entry(input_frame, width=30)
        self.name_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
        
        ttk.Label(input_frame, text="Цена покупки ($):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.buy_entry = ttk.Entry(input_frame, width=15)
        self.buy_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(input_frame, text="Цена продажи ($):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.sell_entry = ttk.Entry(input_frame, width=15)
        self.sell_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Кнопка добавления изображения
        self.img_btn = ttk.Button(input_frame, text="Добавить фото", command=self.add_image)
        self.img_btn.grid(row=3, column=0, pady=5)
        
        self.img_label = ttk.Label(input_frame, text="Фото не выбрано", foreground="gray")
        self.img_label.grid(row=3, column=1, sticky=tk.W, padx=5)
        
        # Превью изображения ввода
        self.image_preview = ttk.Label(input_frame)
        self.image_preview.grid(row=4, column=0, columnspan=2, pady=5)
        
        # Кнопки действий
        btn_frame = ttk.Frame(input_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Рассчитать", command=self.calculate).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Добавить сделку", command=self.add_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Очистить", command=self.clear_fields).pack(side=tk.LEFT, padx=5)
        
        # Результат расчета
        self.result_label = ttk.Label(input_frame, text="", font=("Arial", 12, "bold"))
        self.result_label.grid(row=6, column=0, columnspan=2, pady=5)
        
        # Превью выбранного товара (правый верхний угол)
        self.selected_image_label = ttk.Label(self.preview_frame, text="Выберите товар из истории")
        self.selected_image_label.pack(pady=10)
        
        self.selected_image = ttk.Label(self.preview_frame)
        self.selected_image.pack()
        
        # Поля для редактирования выбранного товара
        edit_frame = ttk.Frame(self.preview_frame)
        edit_frame.pack(pady=10)
        
        ttk.Label(edit_frame, text="Новая цена продажи:").grid(row=0, column=0, sticky=tk.W)
        self.edit_sell_entry = ttk.Entry(edit_frame, width=15)
        self.edit_sell_entry.grid(row=0, column=1, padx=5)
        
        self.edit_btn = ttk.Button(
            edit_frame, 
            text="Обновить цену", 
            command=self.update_product_price,
            state=tk.DISABLED
        )
        self.edit_btn.grid(row=1, column=0, columnspan=2, pady=5)
        
        # Таблица истории
        columns = ("№", "Товар", "Покупка", "Продажа", "Прибыль", "Дата")
        self.history_tree = ttk.Treeview(
            history_frame, 
            columns=columns, 
            show="headings",
            selectmode="browse",
            height=12
        )
        
        # Настройка столбцов
        col_widths = [40, 150, 80, 80, 100, 120]
        for col, width in zip(columns, col_widths):
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=width, anchor=tk.CENTER)
        
        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Привязка события выбора
        self.history_tree.bind("<<TreeviewSelect>>", self.on_product_select)
        
        # Кнопки управления историей
        history_btn_frame = ttk.Frame(history_frame)
        history_btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(
            history_btn_frame, 
            text="Обновить историю", 
            command=self.update_history
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            history_btn_frame, 
            text="Удалить выбранное", 
            command=self.delete_product
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            history_btn_frame, 
            text="Очистить историю", 
            command=self.clear_history
        ).pack(side=tk.RIGHT, padx=5)
        
        # Статистика
        stats_frame = ttk.Frame(history_frame)
        stats_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.stats_label = ttk.Label(
            stats_frame, 
            text="Всего сделок: 0 | Прибыль: $0.00", 
            font=("Arial", 10, "bold")
        )
        self.stats_label.pack()
        
        # Заполняем историю
        self.update_history()
    
    def on_product_select(self, event):
        selected = self.history_tree.selection()
        if not selected:
            return
            
        item = self.history_tree.item(selected[0])
        values = item['values']
        index = int(values[0]) - 1
        
        if 0 <= index < len(self.products):
            self.selected_product_index = index
            product = self.products[index]
            
            # Показываем фото товара
            self.show_selected_product_image(product)
            
            # Заполняем поле для редактирования
            self.edit_sell_entry.delete(0, tk.END)
            self.edit_sell_entry.insert(0, f"{product['sell_price']:.2f}")
            self.edit_btn.config(state=tk.NORMAL)
    
    def show_selected_product_image(self, product):
        self.selected_image_label.config(text=product['name'])
        
        if product.get('image') and os.path.exists(product['image']):
            try:
                img = Image.open(product['image'])
                img.thumbnail((300, 300))
                photo = ImageTk.PhotoImage(img)
                self.selected_image.config(image=photo)
                self.selected_image.image = photo
            except Exception as e:
                self.selected_image.config(image='')
                self.selected_image_label.config(text=f"Ошибка загрузки изображения\n{str(e)}")
        else:
            self.selected_image.config(image='')
            self.selected_image_label.config(text="Нет изображения")
    
    def update_product_price(self):
        if self.selected_product_index is None:
            return
            
        try:
            new_price = float(self.edit_sell_entry.get())
            if new_price < 0:
                raise ValueError("Цена не может быть отрицательной")
                
            self.products[self.selected_product_index]['sell_price'] = new_price
            self.save_data()
            self.update_history()
            messagebox.showinfo("Успех", "Цена продажи обновлена")
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректная цена: {str(e)}")
    
    def add_image(self):
        file_path = filedialog.askopenfilename(
            title="Выберите изображение товара",
            filetypes=[("Изображения", "*.png *.jpg *.jpeg"), ("Все файлы", "*.*")]
        )
        
        if file_path:
            try:
                img = Image.open(file_path)
                img.thumbnail((200, 200))
                
                self.current_image = {
                    "path": file_path,
                    "image": img,
                    "photo": ImageTk.PhotoImage(img)
                }
                
                self.img_label.config(text=os.path.basename(file_path))
                self.image_preview.config(image=self.current_image["photo"])
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить изображение:\n{str(e)}")
    
    def calculate(self):
        try:
            buy_price = float(self.buy_entry.get())
            sell_price = float(self.sell_entry.get())
            
            profit = sell_price - buy_price
            profit_percent = (profit / buy_price) * 100 if buy_price != 0 else 0
            
            if profit >= 0:
                result_text = f"Прибыль: +${profit:.2f} (+{profit_percent:.1f}%)"
                color = "green"
            else:
                result_text = f"Убыток: ${profit:.2f} ({profit_percent:.1f}%)"
                color = "red"
            
            self.result_label.config(text=result_text, foreground=color)
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числовые значения цен")
    
    def add_product(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Ошибка", "Введите название товара")
            return
        
        try:
            buy_price = float(self.buy_entry.get())
            sell_price = float(self.sell_entry.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные цены")
            return
        
        product = {
            "name": name,
            "buy_price": buy_price,
            "sell_price": sell_price,
            "image": self.current_image["path"] if self.current_image else "",
            "date": datetime.now().strftime("%d.%m.%Y %H:%M")
        }
        
        self.products.append(product)
        self.save_data()
        self.update_history()
        self.clear_fields()
        messagebox.showinfo("Успех", "Сделка добавлена в историю")
    
    def update_history(self):
        self.history_tree.delete(*self.history_tree.get_children())
        
        total_profit = 0
        for i, product in enumerate(self.products, 1):
            profit = product["sell_price"] - product["buy_price"]
            total_profit += profit
            
            if profit >= 0:
                profit_text = f"+${profit:.2f}"
                profit_color = "#006400"  # Темно-зеленый
            else:
                profit_text = f"-${abs(profit):.2f}"
                profit_color = "#8B0000"  # Темно-красный
            
            self.history_tree.insert("", tk.END, values=(
                i,
                product["name"],
                f"${product['buy_price']:.2f}",
                f"${product['sell_price']:.2f}",
                profit_text,
                product["date"]
            ), tags=(profit_color,))
        
        # Обновляем статистику
        self.stats_label.config(
            text=f"Всего сделок: {len(self.products)} | Общая прибыль: ${total_profit:.2f}",
            foreground="#006400" if total_profit >= 0 else "#8B0000"
        )
        
        # Сбрасываем выбор товара
        self.selected_product_index = None
        self.selected_image_label.config(text="Выберите товар из истории")
        self.selected_image.config(image='')
        self.edit_sell_entry.delete(0, tk.END)
        self.edit_btn.config(state=tk.DISABLED)
    
    def delete_product(self):
        selected = self.history_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите сделку для удаления")
            return
        
        index = int(self.history_tree.item(selected[0], "values")[0]) - 1
        self.products.pop(index)
        self.save_data()
        self.update_history()
    
    def clear_history(self):
        if not messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            return
        
        self.products = []
        self.save_data()
        self.update_history()
    
    def clear_fields(self):
        self.name_entry.delete(0, tk.END)
        self.buy_entry.delete(0, tk.END)
        self.sell_entry.delete(0, tk.END)
        self.result_label.config(text="")
        self.img_label.config(text="Фото не выбрано", foreground="gray")
        self.image_preview.config(image="")
        self.current_image = None
    
    def save_data(self):
        try:
            with open("smoke_calculator_data.json", "w", encoding="utf-8") as f:
                json.dump(self.products, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные:\n{str(e)}")
    
    def load_data(self):
        try:
            with open("smoke_calculator_data.json", "r", encoding="utf-8") as f:
                self.products = json.load(f)
        except FileNotFoundError:
            self.products = []
        except json.JSONDecodeError:
            messagebox.showerror("Ошибка", "Файл данных поврежден, создан новый")
            self.products = []
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные:\n{str(e)}")
            self.products = []

if __name__ == "__main__":
    root = tk.Tk()
    app = SmokeCalculator(root)
    root.mainloop()
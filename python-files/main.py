import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import json

class SmokeCalculatorApp:
    def init(self, root):
        self.root = root
        self.root.title("GTA 5 RP Перекур Калькулятор")
        self.root.geometry("600x500")
        
        # Данные о товарах
        self.products = []
        self.load_data()
        
        # Переменные
        self.image_path = tk.StringVar()
        self.product_name = tk.StringVar()
        self.buy_price = tk.DoubleVar()
        self.sell_price = tk.DoubleVar()
        
        # Создание интерфейса
        self.create_widgets()
        
    def create_widgets(self):
        # Фрейм для ввода данных
        input_frame = tk.LabelFrame(self.root, text="Данные о товаре", padx=10, pady=10)
        input_frame.pack(pady=10, padx=10, fill="x")
        
        # Поля ввода
        tk.Label(input_frame, text="Название товара:").grid(row=0, column=0, sticky="w")
        tk.Entry(input_frame, textvariable=self.product_name).grid(row=0, column=1, sticky="ew")
        
        tk.Label(input_frame, text="Цена покупки:").grid(row=1, column=0, sticky="w")
        tk.Entry(input_frame, textvariable=self.buy_price).grid(row=1, column=1, sticky="ew")
        
        tk.Label(input_frame, text="Цена продажи:").grid(row=2, column=0, sticky="w")
        tk.Entry(input_frame, textvariable=self.sell_price).grid(row=2, column=1, sticky="ew")
        
        # Кнопка добавления изображения
        tk.Button(input_frame, text="Добавить фото", command=self.add_image).grid(row=3, column=0, pady=5)
        self.image_label = tk.Label(input_frame, text="Фото не выбрано")
        self.image_label.grid(row=3, column=1, sticky="w")
        
        # Кнопки управления
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Рассчитать", command=self.calculate).pack(side="left", padx=5)
        tk.Button(button_frame, text="Добавить товар", command=self.add_product).pack(side="left", padx=5)
        tk.Button(button_frame, text="История", command=self.show_history).pack(side="left", padx=5)
        tk.Button(button_frame, text="Очистить", command=self.clear_fields).pack(side="left", padx=5)
        
        # Поле для вывода результата
        self.result_label = tk.Label(self.root, text="", font=("Arial", 12))
        self.result_label.pack(pady=10)
        
        # Превью изображения
        self.image_preview = tk.Label(self.root)
        self.image_preview.pack()
        
    def add_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
        )
        if file_path:
            self.image_path.set(file_path)
            self.image_label.config(text=os.path.basename(file_path))
            
            # Показываем превью
            img = Image.open(file_path)
            img.thumbnail((200, 200))
            photo = ImageTk.PhotoImage(img)
            self.image_preview.config(image=photo)
            self.image_preview.image = photo
    
    def calculate(self):
        try:
            buy = self.buy_price.get()
            sell = self.sell_price.get()
            profit = sell - buy
            
            if profit >= 0:
                result_text = f"Прибыль: +${profit:.2f}"
                color = "green"
            else:
                result_text = f"Убыток: {profit:.2f}"
                color = "red"
                
            self.result_label.config(text=result_text, fg=color)
        except:
            messagebox.showerror("Ошибка", "Проверьте введенные данные")
    
    def add_product(self):
        if not self.product_name.get():
            messagebox.showerror("Ошибка", "Введите название товара")
return
            
        product = {
            "name": self.product_name.get(),
            "buy_price": self.buy_price.get(),
            "sell_price": self.sell_price.get(),
            "image": self.image_path.get(),
            "timestamp": tk.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.products.append(product)
        self.save_data()
        messagebox.showinfo("Успех", "Товар добавлен в историю")
        self.clear_fields()
    
    def show_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("История товаров")
        history_window.geometry("800x600")
        
        for idx, product in enumerate(self.products):
            frame = tk.Frame(history_window, bd=2, relief="groove", padx=10, pady=10)
            frame.pack(fill="x", padx=5, pady=5)
            
            # Показываем изображение если есть
            if product["image"] and os.path.exists(product["image"]):
                try:
                    img = Image.open(product["image"])
                    img.thumbnail((100, 100))
                    photo = ImageTk.PhotoImage(img)
                    img_label = tk.Label(frame, image=photo)
                    img_label.image = photo
                    img_label.grid(row=0, column=0, rowspan=4)
                except:
                    pass
            
            # Информация о товаре
            tk.Label(frame, text=f"Товар: {product['name']}").grid(row=0, column=1, sticky="w")
            tk.Label(frame, text=f"Куплено за: ${product['buy_price']:.2f}").grid(row=1, column=1, sticky="w")
            tk.Label(frame, text=f"Продано за: ${product['sell_price']:.2f}").grid(row=2, column=1, sticky="w")
            
            profit = product["sell_price"] - product["buy_price"]
            if profit >= 0:
                profit_text = f"Прибыль: +${profit:.2f}"
                profit_color = "green"
            else:
                profit_text = f"Убыток: {profit:.2f}"
                profit_color = "red"
                
            tk.Label(frame, text=profit_text, fg=profit_color).grid(row=3, column=1, sticky="w")
            tk.Label(frame, text=product["timestamp"]).grid(row=0, column=2, sticky="e")
            
            # Кнопка удаления
            tk.Button(frame, text="Удалить", command=lambda i=idx: self.delete_product(i)).grid(row=3, column=2)
    
    def delete_product(self, index):
        self.products.pop(index)
        self.save_data()
        messagebox.showinfo("Успех", "Товар удален из истории")
        self.show_history()
    
    def clear_fields(self):
        self.product_name.set("")
        self.buy_price.set(0.0)
        self.sell_price.set(0.0)
        self.image_path.set("")
        self.image_label.config(text="Фото не выбрано")
        self.result_label.config(text="")
        self.image_preview.config(image="")
        self.image_preview.image = None
    
    def save_data(self):
        with open("products.json", "w") as f:
            json.dump(self.products, f)
    
    def load_data(self):
        try:
            with open("products.json", "r") as f:
                self.products = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.products = []

if name == "main":
    root = tk.Tk()
    app = SmokeCalculatorApp(root)
    root.mainloop()
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import os
import csv

class CSVGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор CSV для маркировки товаров")
        self.root.geometry("700x500")
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Настройка шрифтов
        self.big_font = ('Arial', 12)
        self.normal_font = ('Arial', 10)
        
        # Основной фрейм
        main_frame = ttk.Frame(root, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Заголовок
        header = ttk.Label(
            main_frame, 
            text="Генератор CSV для товарной маркировки",
            font=('Arial', 14, 'bold'),
            foreground='#2c3e50'
        )
        header.pack(pady=(0, 20))
        
        # Фрейм для файлов
        file_frame = ttk.LabelFrame(main_frame, text="Файлы", padding=15)
        file_frame.pack(fill='x', pady=10)
        
        # Поле для XLS файла
        ttk.Label(file_frame, text="XLS файл с товарами:", font=self.normal_font).grid(row=0, column=0, sticky='w', pady=5)
        self.xls_path = ttk.Entry(file_frame, width=60, font=self.normal_font)
        self.xls_path.grid(row=0, column=1, padx=10, pady=5, sticky='we')
        ttk.Button(file_frame, text="Обзор", command=self.browse_xls, width=10).grid(row=0, column=2, pady=5)

        # Поле для CSV файла с маркировкой
        ttk.Label(file_frame, text="CSV файл с маркировкой:", font=self.normal_font).grid(row=1, column=0, sticky='w', pady=5)
        self.csv_path = ttk.Entry(file_frame, width=60, font=self.normal_font)
        self.csv_path.grid(row=1, column=1, padx=10, pady=5, sticky='we')
        ttk.Button(file_frame, text="Обзор", command=self.browse_csv, width=10).grid(row=1, column=2, pady=5)

        # Настройки
        settings_frame = ttk.LabelFrame(main_frame, text="Настройки", padding=15)
        settings_frame.pack(fill='x', pady=10)

        ttk.Label(settings_frame, text="Ставка НДС (%):", font=self.normal_font).grid(row=0, column=0, sticky='w', pady=5)
        self.vat_rate = ttk.Entry(settings_frame, width=10, font=self.normal_font)
        self.vat_rate.insert(0, "20")
        self.vat_rate.grid(row=0, column=1, sticky='w', padx=10)

        # Кнопка генерации
        self.generate_btn = ttk.Button(
            main_frame,
            text="Сгенерировать CSV",
            command=self.generate_csv,
            style='Accent.TButton'
        )
        self.generate_btn.pack(pady=20)

        # Настройка стиля для кнопки
        self.style.configure('Accent.TButton', background='#3498db', foreground='white', font=('Arial', 11,'bold'))

        # Прогресс-бар
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.pack(fill='x', pady=5)

        # Статус-бар
        self.status = ttk.Label(
            main_frame,
            text="Готово к работе",
            relief='sunken',
            anchor='center',
            padding=10,
            font=self.normal_font
        )
        self.status.pack(fill='x', pady=(20, 0))
        
        # Настройка веса колонок для адаптивности
        file_frame.columnconfigure(1, weight=1)

    def browse_xls(self):
        """Обработка выбора XLS файла"""
        file_path = filedialog.askopenfilename(
            title="Выберите XLS файл",
            filetypes=[("Excel files", "*.xls *.xlsx")]
        )
        if file_path:
            self.xls_path.delete(0, tk.END)
            self.xls_path.insert(0, file_path)
            self.status["text"] = f"Выбран XLS файл: {os.path.basename(file_path)}"

    def browse_csv(self):
        """Обработка выбора CSV файла"""
        file_path = filedialog.askopenfilename(
            title="Выберите CSV файл",
            filetypes=[("CSV files", "*.csv")]
        )
        if file_path:
            self.csv_path.delete(0, tk.END)
            self.csv_path.insert(0, file_path)
            self.status["text"] = f"Выбран CSV файл: {os.path.basename(file_path)}"

    def generate_csv(self):
       """Основная функция генерации CSV"""
       # Обновляем прогресс и статус
       self.progress["value"] = 0
       self.status["text"] = "Начата обработка данных..."
       self.root.update()

       # Проверка обязательных файлов
       if not self.xls_path.get():
           messagebox.showerror("Ошибка", "Пожалуйста, выберите XLS файл с товарами!")
           return
       if not self.csv_path.get():
           messagebox.showerror("Ошибка", "Пожалуйста, выберите CSV файл с маркировкой!")
           return

       # Проверка ставки НДС
       try:
           vat_str = self.vat_rate.get()
           if not vat_str.isdigit():
               raise ValueError("НДС должен быть числом")
           vat_value = int(vat_str)
       except Exception as e:
           messagebox.showerror("Ошибка", f"Некорректная ставка НДС: {e}")
           return

       # Загрузка XLS файла с товарами
       try:
           self.status["text"] = "Чтение XLS файла..."
           self.root.update()

           xls_df = pd.read_excel(
               self.xls_path.get(),
               header=None,
               usecols=[0, 1 ,2],
               names=["name", "price", "quantity"],
               dtype={"name": str,"price": float,"quantity": int}
           )
           xls_df.dropna(how="all", inplace=True)  # Удаляем полностью пустые строки

           # Очистка названий товаров от табов и пробелов
           xls_df['name'] = xls_df['name'].astype(str).str.replace('\t',' ').str.strip()

           total_products = len(xls_df)

           self.progress["value"] = 20
           self.status["text"] = f"Загружено товаров: {total_products}"
           self.root.update()
       except Exception as e:
           messagebox.showerror("Ошибка", f"Ошибка чтения XLS файла: {e}")
           return

       # Обработка CSV файла с маркировкой (КИЗ)
       try:
           self.status["text"] = "Обработка CSV файла..."
           self.root.update()

           with open(self.csv_path.get(), 'r', encoding='utf-8') as f:
               content = f.read()

           codes_list = []
           for line in content.splitlines():
               line_cleaned = line.strip('\n\r')
               if line_cleaned.startswith('\ufeff'):
                   line_cleaned = line_cleaned[1:]
               if line_cleaned:
                   codes_list.append(line_cleaned)

           total_codes = len(codes_list)

           self.progress["value"] = 40
           self.status["text"] = f"Загружено КИЗ: {total_codes}"
           self.root.update()
       except Exception as e:
           messagebox.showerror("Ошибка", f"Ошибка обработки CSV файла: {e}")
           return

       # Запрос места сохранения результата
       save_path = filedialog.asksaveasfilename(
           title="Сохранить результат",
           defaultextension=".csv",
           filetypes=[("CSV files", "*.csv")]
       )
       if not save_path:
           self.status["text"] ="Операция отменена"
           return

       try:
          """Создание итогового CSV"""
          with open(save_path,"w",encoding='utf-8',newline='') as f:
              writer = csv.writer(f)
              processed_items = 0
              used_codes_count = 0

              for idx,row in enumerate(xls_df.itertuples(), start=1):
                  code_index = idx - 1  # индекс в списке кодов

                  code_value =""
                  if code_index < total_codes:
                      code_value=codes_list[code_index]
                      used_codes_count +=1

                  product_data=[
                      idx,
                      row.name,
                      f"{row.price:.2f}",
                      int(row.quantity),
                      796,
                      f"{vat_value}%",
                      "КИЗ"
                  ]

                  # Обработка кода (экранирование кавычек и оборачивание в кавычки при необходимости)
                  if code_value:
                      code_value_escaped = code_value
                  else:
                      code_value_escaped=""
                  
                  product_data.append(code_value_escaped)

                  writer.writerow(product_data)

                  processed_items +=1

                  # Обновление прогресса (от 40 до 100%)
                  progress_percent=(40 + (idx / len(xls_df)) *60)
                  if progress_percent>100:
                      progress_percent=100

                  self.progress["value"]=progress_percent
                  status_text=f"Обработка: {idx}/{len(xls_df)} товаров," \
                              f" использовано кодов: {used_codes_count}"
                  self.status["text"]=status_text
                  self.root.update()

          # Завершение процесса
          self.progress["value"]=100

          success_msg=f"""Файл успешно сгенерирован!
          
• Обработано товаров: {processed_items}
• Использовано КИЗ: {used_codes_count} из {total_codes}
• Файл сохранен: {os.path.basename(save_path)}"""

          self.status["text"]=f"Готово! {processed_items} товаров , {used_codes_count} кодов"
          messagebox.showinfo("Успех",success_msg)

       except Exception as e:
          messagebox.showerror("Ошибка",f"Ошибка при создании файла:{e}")
          self.status["text"]="Ошибка:"+str(e)


if __name__=="__main__":
    root=tk.Tk()
    app=CSVGeneratorApp(root)
    root.mainloop()
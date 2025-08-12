import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import requests
import os
import time
from datetime import datetime

class WBQuestionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WB Questions Manager")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Настройка стилей
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        self.style.configure("Header.TLabel", background="#2c3e50", foreground="white", font=("Arial", 12, "bold"))
        self.style.configure("TButton", font=("Arial", 10))
        self.style.configure("TEntry", font=("Arial", 10))
        
        # Главный фрейм
        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Заголовок
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        ttk.Label(header_frame, text="Wildberries Questions Manager", style="Header.TLabel").pack(fill=tk.X, padx=10, pady=10)
        
        # Секция API ключа
        api_frame = ttk.LabelFrame(main_frame, text="Авторизация Wildberries")
        api_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(api_frame, text="API Key:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.api_key = ttk.Entry(api_frame, width=60)
        self.api_key.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        # Кнопка помощи для API ключа
        ttk.Button(api_frame, text="Где взять API ключ?", 
                  command=self.show_api_help).grid(row=0, column=2, padx=5, pady=5)
        
        # Секция загрузки вопросов
        download_frame = ttk.LabelFrame(main_frame, text="Загрузка вопросов")
        download_frame.pack(fill=tk.X, pady=5)
        
        self.download_btn = ttk.Button(download_frame, text="Скачать вопросы в Excel", 
                                      command=self.download_questions, width=25)
        self.download_btn.pack(pady=10)
        
        # Секция отправки ответов
        upload_frame = ttk.LabelFrame(main_frame, text="Отправка ответов")
        upload_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(upload_frame, text="Файл с ответами:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.file_path = ttk.Entry(upload_frame, width=50)
        self.file_path.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.file_path.config(state='disabled')
        
        ttk.Button(upload_frame, text="Обзор", command=self.browse_file).grid(row=0, column=2, padx=5, pady=5)
        
        self.upload_btn = ttk.Button(upload_frame, text="Отправить ответы", 
                                    command=self.send_answers, width=25)
        self.upload_btn.grid(row=1, column=0, columnspan=3, pady=10)
        
        # Журнал
        log_frame = ttk.LabelFrame(main_frame, text="Журнал операций")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, state='disabled')
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Статус бар
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе")
        status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Информация
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=10)
        ttk.Label(info_frame, text="Приложение для работы с вопросами покупателей Wildberries", 
                 foreground="#7f8c8d", font=("Arial", 9)).pack(side=tk.LEFT)
        ttk.Label(info_frame, text="v1.0", foreground="#7f8c8d", font=("Arial", 9)).pack(side=tk.RIGHT)
        
        # Логирование
        self.log_message("Приложение запущено. Введите API ключ Wildberries")
        
    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        self.status_var.set(message)
        self.root.update()
        
    def show_api_help(self):
        help_text = """
        Как получить API ключ Wildberries:
        1. Перейдите в Личный кабинет Wildberries (https://seller.wildberries.ru/)
        2. Откройте раздел "Настройки" -> "Доступ к API"
        3. Скопируйте "Стандартный API-ключ"
        4. Вставьте ключ в поле выше
        """
        messagebox.showinfo("Где взять API ключ?", help_text)
        
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Выберите файл с ответами",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if filename:
            self.file_path.config(state='normal')
            self.file_path.delete(0, tk.END)
            self.file_path.insert(0, filename)
            self.file_path.config(state='disabled')
            self.log_message(f"Выбран файл: {filename}")
        
    def download_questions(self):
        api_key = self.api_key.get().strip()
        if not api_key:
            messagebox.showerror("Ошибка", "Введите API ключ Wildberries")
            return
            
        try:
            self.log_message("Начало загрузки вопросов...")
            
            # Получаем вопросы через API
            questions = self.fetch_questions(api_key)
            
            if not questions:
                self.log_message("Не найдено неотвеченных вопросов")
                messagebox.showinfo("Информация", "Не найдено неотвеченных вопросов")
                return
                
            # Создаем DataFrame
            df = pd.DataFrame(questions)
            
            # Сохраняем в Excel
            save_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile="wb_questions.xlsx"
            )
            
            if not save_path:
                self.log_message("Сохранение отменено")
                return
                
            df.to_excel(save_path, index=False)
            self.log_message(f"Сохранено: {save_path} ({len(df)} вопросов)")
            messagebox.showinfo("Успех", f"Вопросы успешно сохранены в файл:\n{save_path}")
            
        except Exception as e:
            self.log_message(f"Ошибка: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось загрузить вопросы:\n{str(e)}")
        
    def fetch_questions(self, api_key):
        url = "https://feedbacks-api.wildberries.ru/api/v1/questions"
        headers = {"Authorization": api_key}
        params = {"isAnswered": False, "take": 1000}
        
        self.log_message("Запрос к API Wildberries...")
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            error_msg = response.json().get('message', 'Неизвестная ошибка')
            raise Exception(f"Ошибка API: {error_msg} (код {response.status_code})")
        
        data = response.json()
        questions = []
        
        for q in data.get('data', {}).get('questions', []):
            questions.append({
                "ID": q['id'],
                "Дата": q['createdDate'],
                "Артикул": q.get('productDetails', {}).get('supplierArticle', ''),
                "Текст вопроса": q['text'],
                "Ответ": "",
                "Статус": "Отвечен" if q['answer'] else "Не отвечен"
            })
            
        self.log_message(f"Получено {len(questions)} вопросов")
        return questions
        
    def send_answers(self):
        api_key = self.api_key.get().strip()
        filename = self.file_path.get()
        
        if not api_key:
            messagebox.showerror("Ошибка", "Введите API ключ Wildberries")
            return
            
        if not filename or not os.path.exists(filename):
            messagebox.showerror("Ошибка", "Выберите файл с ответами")
            return
            
        try:
            self.log_message("Чтение файла с ответами...")
            
            # Читаем Excel файл
            df = pd.read_excel(filename)
            
            # Проверяем необходимые колонки
            required_cols = ["ID", "Ответ"]
            if not all(col in df.columns for col in required_cols):
                missing = [col for col in required_cols if col not in df.columns]
                raise Exception(f"Отсутствуют обязательные колонки: {', '.join(missing)}")
                
            # Фильтруем только строки с ответами
            df = df[df['Ответ'].notna() & (df['Ответ'] != "")]
            
            if len(df) == 0:
                self.log_message("Нет ответов для отправки")
                messagebox.showinfo("Информация", "В файле нет ответов для отправки")
                return
                
            self.log_message(f"Найдено {len(df)} ответов для отправки")
            
            # Отправляем ответы
            success_count = 0
            error_count = 0
            
            for index, row in df.iterrows():
                try:
                    self.answer_question(
                        api_key=api_key,
                        question_id=row['ID'],
                        answer_text=str(row['Ответ'])
                    )
                    success_count += 1
                    self.log_message(f"Отправлен ответ на вопрос ID: {row['ID']}")
                except Exception as e:
                    error_count += 1
                    self.log_message(f"Ошибка для вопроса ID {row['ID']}: {str(e)}")
                
                # Небольшая задержка для избежания блокировки
                time.sleep(0.2)
                self.root.update()
                
            self.log_message(f"Отправка завершена: успешно {success_count}, ошибок {error_count}")
            messagebox.showinfo(
                "Результат", 
                f"Ответы отправлены!\nУспешно: {success_count}\nОшибок: {error_count}"
            )
            
        except Exception as e:
            self.log_message(f"Ошибка: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось отправить ответы:\n{str(e)}")
        
    def answer_question(self, api_key, question_id, answer_text):
        url = f"https://feedbacks-api.wildberries.ru/api/v1/questions/{question_id}/answer"
        headers = {
            "Authorization": api_key,
            "Content-Type": "application/json"
        }
        
        # Ограничиваем длину ответа (1000 символов для вопросов)
        answer_text = answer_text[:1000]
        
        data = {
            "text": answer_text,
            "visible": True  # Ответ будет виден всем
        }
        
        response = requests.patch(url, headers=headers, json=data)
        
        if response.status_code != 200:
            error_msg = response.json().get('message', 'Неизвестная ошибка')
            raise Exception(f"Ошибка API: {error_msg} (код {response.status_code})")

if __name__ == "__main__":
    root = tk.Tk()
    app = WBQuestionApp(root)
    root.mainloop()
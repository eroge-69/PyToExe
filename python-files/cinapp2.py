import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, Canvas, Frame, PhotoImage
from datetime import datetime, timedelta
import sqlite3
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import qrcode
from PIL import Image, ImageTk
import os
import csv

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('cinema.db')
    c = conn.cursor()
    
    # Таблица фильмов
    c.execute('''CREATE TABLE IF NOT EXISTS movies (
                 id INTEGER PRIMARY KEY,
                 title TEXT NOT NULL,
                 start_time TEXT NOT NULL,
                 hall INTEGER NOT NULL,
                 price REAL NOT NULL,
                 duration INTEGER NOT NULL,
                 occupied INTEGER DEFAULT 0)''')
    
    # Таблица бронирований
    c.execute('''CREATE TABLE IF NOT EXISTS bookings (
                 id INTEGER PRIMARY KEY,
                 movie_id INTEGER,
                 seat TEXT,
                 status TEXT,  -- 'booked', 'paid'
                 booking_time TEXT,
                 payment_data TEXT,
                 FOREIGN KEY(movie_id) REFERENCES movies(id))''')
    
    # Пользователи
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 username TEXT PRIMARY KEY,
                 password TEXT,
                 role TEXT)''')
    
    # Стандартный пользователь
    try:
        c.execute("INSERT INTO users VALUES (?, ?, ?)", ('admin', 'admin', 'staff'))
    except sqlite3.IntegrityError:
        pass
    
    # Тестовые фильмы
    movies = [
        ('Матрица', '2023-12-15 18:00', 1, 350, 150),
        ('Аватар', '2023-12-15 20:30', 2, 400, 180),
        ('Интерстеллар', '2023-12-16 19:00', 3, 380, 169)
    ]
    
    for movie in movies:
        c.execute('''INSERT OR IGNORE INTO movies 
                     (title, start_time, hall, price, duration) 
                     VALUES (?, ?, ?, ?, ?)''', movie)
    
    conn.commit()
    conn.close()

init_db()

class CinemaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Кинотеатр 'Луч'")
        self.root.geometry("800x600")
        self.current_user = None
        self.show_login_screen()
    
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def show_login_screen(self):
        self.clear_window()
        tk.Label(self.root, text="Кинотеатр 'Луч'", font=("Arial", 24)).pack(pady=20)
        
        tk.Button(self.root, text="Сотрудник", font=("Arial", 16), 
                  command=lambda: self.authenticate('staff'), height=2, width=20).pack(pady=10)
        
        tk.Button(self.root, text="Покупатель", font=("Arial", 16), 
                  command=lambda: self.authenticate('customer'), height=2, width=20).pack(pady=10)
    
    def authenticate(self, role):
        if role == 'customer':
            self.current_user = {'role': 'customer'}
            self.show_main_screen()
            return
        
        # Проверка для сотрудника
        conn = sqlite3.connect('cinema.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username='admin'")
        user = c.fetchone()
        conn.close()
        
        if not user:
            messagebox.showerror("Ошибка", "Администратор не найден")
            return
        
        password = simpledialog.askstring("Авторизация", "Введите пароль:", show='*')
        if password == user[1]:
            self.current_user = {'username': user[0], 'role': user[2]}
            self.show_main_screen()
        else:
            messagebox.showerror("Ошибка", "Неверный пароль")
    
    def show_main_screen(self):
        self.clear_window()
        title = "Панель сотрудника" if self.current_user['role'] == 'staff' else "Бронирование билетов"
        tk.Label(self.root, text=title, font=("Arial", 20)).pack(pady=10)
        
        # Кнопки для сотрудника
        if self.current_user['role'] == 'staff':
            tk.Button(self.root, text="Управление фильмами", 
                      command=self.manage_movies, height=2, width=25).pack(pady=5)
            
            tk.Button(self.root, text="Просмотр статистики", 
                      command=self.show_statistics, height=2, width=25).pack(pady=5)
            
            tk.Button(self.root, text="Выход", 
                      command=self.show_login_screen, height=2, width=25).pack(pady=20)
        
        # Кнопки для покупателя
        else:
            tk.Button(self.root, text="Просмотреть фильмы", 
                      command=self.view_movies, height=2, width=25).pack(pady=5)
            
            tk.Button(self.root, text="Мои бронирования", 
                      command=self.view_bookings, height=2, width=25).pack(pady=5)
            
            tk.Button(self.root, text="Назад", 
                      command=self.show_login_screen, height=2, width=25).pack(pady=20)
    
    def manage_movies(self):
        self.clear_window()
        tk.Label(self.root, text="Управление фильмами", font=("Arial", 18)).pack(pady=10)
        
        # Таблица с фильмами
        columns = ("ID", "Название", "Начало", "Зал", "Цена", "Длительность", "Занято")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80, anchor=tk.CENTER)
        
        self.tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Заполнение данными
        conn = sqlite3.connect('cinema.db')
        c = conn.cursor()
        c.execute("SELECT * FROM movies")
        for row in c.fetchall():
            self.tree.insert("", tk.END, values=row)
        conn.close()
        
        # Кнопки управления
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Добавить", command=self.add_movie).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Редактировать", command=self.edit_movie).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Удалить", command=self.delete_movie).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Назад", command=self.show_main_screen).pack(side=tk.LEFT, padx=5)
    
    def add_movie(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить фильм")
        dialog.geometry("400x300")
        
        fields = [
            ("Название:", tk.Entry(dialog, width=25)),
            ("Начало (ГГГГ-ММ-ДД ЧЧ:ММ):", tk.Entry(dialog, width=25)),
            ("Зал (1-3):", tk.Entry(dialog, width=25)),
            ("Цена:", tk.Entry(dialog, width=25)),
            ("Длительность (мин):", tk.Entry(dialog, width=25))
        ]
        
        for i, (label_text, entry) in enumerate(fields):
            tk.Label(dialog, text=label_text).grid(row=i, column=0, padx=10, pady=5, sticky=tk.W)
            entry.grid(row=i, column=1, padx=10, pady=5)
        
        def save():
            data = [entry.get() for _, entry in fields]
            try:
                conn = sqlite3.connect('cinema.db')
                c = conn.cursor()
                c.execute('''INSERT INTO movies 
                          (title, start_time, hall, price, duration) 
                          VALUES (?, ?, ?, ?, ?)''', 
                          (data[0], data[1], int(data[2]), float(data[3]), int(data[4])))
                conn.commit()
                conn.close()
                messagebox.showinfo("Успех", "Фильм добавлен")
                dialog.destroy()
                self.manage_movies()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при добавлении: {str(e)}")
        
        tk.Button(dialog, text="Сохранить", command=save).grid(row=5, column=0, columnspan=2, pady=10)
    
    def edit_movie(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите фильм для редактирования")
            return
        
        item = self.tree.item(selected[0])
        movie_id = item['values'][0]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Редактировать фильм")
        dialog.geometry("400x300")
        
        conn = sqlite3.connect('cinema.db')
        c = conn.cursor()
        c.execute("SELECT * FROM movies WHERE id=?", (movie_id,))
        movie_data = c.fetchone()
        conn.close()
        
        if not movie_data:
            messagebox.showerror("Ошибка", "Фильм не найден")
            dialog.destroy()
            return
        
        fields = [
            ("Название:", tk.Entry(dialog, width=25)),
            ("Начало (ГГГГ-ММ-ДД ЧЧ:ММ):", tk.Entry(dialog, width=25)),
            ("Зал (1-3):", tk.Entry(dialog, width=25)),
            ("Цена:", tk.Entry(dialog, width=25)),
            ("Длительность (мин):", tk.Entry(dialog, width=25))
        ]
        
        for i, (label_text, entry) in enumerate(fields):
            tk.Label(dialog, text=label_text).grid(row=i, column=0, padx=10, pady=5, sticky=tk.W)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entry.insert(0, movie_data[i+1])  # Пропускаем ID
        
        def save():
            data = [entry.get() for _, entry in fields]
            try:
                conn = sqlite3.connect('cinema.db')
                c = conn.cursor()
                c.execute('''UPDATE movies SET 
                          title=?, start_time=?, hall=?, price=?, duration=?
                          WHERE id=?''', 
                          (data[0], data[1], int(data[2]), float(data[3]), int(data[4]), movie_id))
                conn.commit()
                conn.close()
                messagebox.showinfo("Успех", "Фильм обновлен")
                dialog.destroy()
                self.manage_movies()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при обновлении: {str(e)}")
        
        tk.Button(dialog, text="Сохранить", command=save).grid(row=5, column=0, columnspan=2, pady=10)
    
    def delete_movie(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите фильм для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить выбранный фильм?"):
            item = self.tree.item(selected[0])
            movie_id = item['values'][0]
            
            try:
                conn = sqlite3.connect('cinema.db')
                c = conn.cursor()
                c.execute("DELETE FROM movies WHERE id=?", (movie_id,))
                conn.commit()
                conn.close()
                self.manage_movies()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при удалении: {str(e)}")
    
    def view_movies(self):
        self.clear_window()
        tk.Label(self.root, text="Доступные фильмы", font=("Arial", 18)).pack(pady=10)
        
        # Таблица с фильмами
        columns = ("ID", "Название", "Начало", "Зал", "Цена", "Длительность")
        self.movie_tree = ttk.Treeview(self.root, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.movie_tree.heading(col, text=col)
            self.movie_tree.column(col, width=100, anchor=tk.CENTER)
        
        self.movie_tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Заполнение данными
        conn = sqlite3.connect('cinema.db')
        c = conn.cursor()
        c.execute("SELECT id, title, start_time, hall, price, duration FROM movies")
        for row in c.fetchall():
            self.movie_tree.insert("", tk.END, values=row)
        conn.close()
        
        # Кнопки
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Забронировать", command=self.book_movie).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Назад", command=self.show_main_screen).pack(side=tk.LEFT, padx=5)
    
    def book_movie(self):
        selected = self.movie_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите фильм для бронирования")
            return
        
        item = self.movie_tree.item(selected[0])
        self.selected_movie = {
            'id': item['values'][0],
            'title': item['values'][1],
            'hall': item['values'][3],
            'price': item['values'][4],
            'start_time': item['values'][2]
        }
        
        self.show_seat_selection()
    
    def show_seat_selection(self):
        self.clear_window()
        tk.Label(self.root, text=f"Выбор места: {self.selected_movie['title']}", 
                 font=("Arial", 16)).pack(pady=10)
        
        # Создаем холст для схемы зала
        canvas_frame = Frame(self.root)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Заголовок с рядами
        rows = ['A', 'B', 'C']
        seats_per_row = 10
        
        # Получаем текущие бронирования
        conn = sqlite3.connect('cinema.db')
        c = conn.cursor()
        c.execute('''SELECT seat, status FROM bookings 
                  WHERE movie_id=?''', (self.selected_movie['id'],))
        bookings = {row[0]: row[1] for row in c.fetchall()}
        conn.close()
        
        # Создаем кнопки мест
        self.seat_buttons = {}
        for i, row in enumerate(rows):
            tk.Label(canvas_frame, text=f"Ряд {row}", font=("Arial", 10)).grid(row=i, column=0, padx=5, pady=5)
            for j in range(1, seats_per_row + 1):
                seat = f"{row}-{j}"
                status = bookings.get(seat, 'free')
                
                btn = tk.Button(
                    canvas_frame, 
                    text=str(j), 
                    width=2,
                    bg=self.get_seat_color(status),
                    command=lambda s=seat: self.select_seat(s)
                )
                btn.grid(row=i, column=j, padx=2, pady=2)
                self.seat_buttons[seat] = btn
        
        # Кнопки управления
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        self.selected_seat = None
        tk.Label(btn_frame, text="Выбранное место: ").pack(side=tk.LEFT, padx=5)
        self.seat_label = tk.Label(btn_frame, text="---", fg="blue")
        self.seat_label.pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Забронировать", 
                  command=self.confirm_booking, state=tk.DISABLED).pack(side=tk.LEFT, padx=5)
        self.booking_btn = tk.Button(btn_frame, text="Оплатить", 
                  command=self.show_payment, state=tk.DISABLED)
        self.booking_btn.pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Назад", command=self.view_movies).pack(side=tk.LEFT, padx=5)
    
    def get_seat_color(self, status):
        return {
            'free': 'white',
            'booked': 'lightblue',
            'paid': 'lightcoral'
        }.get(status, 'gray')
    
    def select_seat(self, seat):
        conn = sqlite3.connect('cinema.db')
        c = conn.cursor()
        c.execute("SELECT status FROM bookings WHERE movie_id=? AND seat=?", 
                 (self.selected_movie['id'], seat))
        status = c.fetchone()
        conn.close()
        
        if status and status[0] == 'paid':
            messagebox.showinfo("Информация", "Место уже куплено")
            return
        elif status and status[0] == 'booked':
            if messagebox.askyesno("Подтверждение", "Место забронировано. Заменить бронь?"):
                self.selected_seat = seat
                self.seat_label.config(text=seat)
                self.booking_btn.config(state=tk.NORMAL)
        else:
            self.selected_seat = seat
            self.seat_label.config(text=seat)
            self.booking_btn.config(state=tk.NORMAL)
    
    def confirm_booking(self):
        if not self.selected_seat:
            return
        
        conn = sqlite3.connect('cinema.db')
        c = conn.cursor()
        
        # Проверяем существующую бронь
        c.execute('''SELECT id FROM bookings 
                  WHERE movie_id=? AND seat=?''', 
                  (self.selected_movie['id'], self.selected_seat))
        existing = c.fetchone()
        
        # Обновляем или создаем бронь
        if existing:
            c.execute('''UPDATE bookings SET 
                      booking_time=?, status='booked'
                      WHERE id=?''', 
                      (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), existing[0]))
        else:
            c.execute('''INSERT INTO bookings 
                      (movie_id, seat, status, booking_time)
                      VALUES (?, ?, ?, ?)''', 
                      (self.selected_movie['id'], self.selected_seat, 
                       'booked', datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        
        conn.commit()
        conn.close()
        messagebox.showinfo("Успех", "Место забронировано!")
        self.show_seat_selection()
    
    def show_payment(self):
        if not self.selected_seat:
            return
        
        payment_window = tk.Toplevel(self.root)
        payment_window.title("Оплата билета")
        payment_window.geometry("500x400")
        
        fields = [
            ("Номер карты (16 цифр):", tk.Entry(payment_window)),
            ("Срок действия (ММ/ГГ):", tk.Entry(payment_window)),
            ("Имя владельца:", tk.Entry(payment_window)),
            ("CVV/CVC:", tk.Entry(payment_window, show="*")),
            ("ФИО покупателя:", tk.Entry(payment_window))
        ]
        
        for i, (label_text, entry) in enumerate(fields):
            tk.Label(payment_window, text=label_text).grid(row=i, column=0, padx=10, pady=5, sticky=tk.W)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky=tk.EW)
        
        def process_payment():
            # Простейшая валидация
            card_number = fields[0][1].get().replace(" ", "")
            if len(card_number) != 16 or not card_number.isdigit():
                messagebox.showerror("Ошибка", "Неверный номер карты")
                return
            
            # Сохраняем данные оплаты
            payment_data = {
                'card': card_number,
                'expiry': fields[1][1].get(),
                'cardholder': fields[2][1].get(),
                'cvv': fields[3][1].get(),
                'buyer': fields[4][1].get()
            }
            
            conn = sqlite3.connect('cinema.db')
            c = conn.cursor()
            c.execute('''UPDATE bookings SET 
                      status='paid', payment_data=?
                      WHERE movie_id=? AND seat=?''', 
                      (str(payment_data), self.selected_movie['id'], self.selected_seat))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Успех", "Оплата прошла успешно!")
            payment_window.destroy()
            self.generate_ticket(payment_data['buyer'])
        
        tk.Button(payment_window, text="Оплатить", command=process_payment).grid(
            row=len(fields), column=0, columnspan=2, pady=10)
    
    def generate_ticket(self, buyer_name):
        # Создаем информацию для билета
        ticket_info = [
            f"КИНОТЕАТР 'ЛУЧ'",
            f"БИЛЕТ",
            f"Фильм: {self.selected_movie['title']}",
            f"Время: {self.selected_movie['start_time']}",
            f"Зал: {self.selected_movie['hall']}",
            f"Место: {self.selected_seat}",
            f"Цена: {self.selected_movie['price']} руб.",
            f"Покупатель: {buyer_name}",
            f"Дата бронирования: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ]
        
        # Создаем QR-код
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data("\n".join(ticket_info))
        qr.make(fit=True)
        
        # Создаем изображение билета с QR-кодом
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Добавляем текст на изображение
        from PIL import ImageDraw, ImageFont
        
        # Создаем новое изображение с местом для текста
        ticket_img = Image.new('RGB', (400, 600), color='white')
        draw = ImageDraw.Draw(ticket_img)
        
        # Используем стандартный шрифт или загружаем свой
        try:
            font = ImageFont.truetype("arial.ttf", 16)
            font_bold = ImageFont.truetype("arialbd.ttf", 20)
        except:
            font = ImageFont.load_default()
            font_bold = ImageFont.load_default()
        
        # Добавляем текст
        y_position = 20
        for i, line in enumerate(ticket_info):
            current_font = font_bold if i in [0, 1] else font
            draw.text((20, y_position), line, fill="black", font=current_font)
            y_position += 30 if i in [0, 1] else 25
        
        # Вставляем QR-код
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img = qr_img.resize((200, 200))
        ticket_img.paste(qr_img, (100, y_position + 20))
        
        # Сохраняем изображение
        ticket_filename = f"ticket_{self.selected_movie['id']}_{self.selected_seat}.png"
        ticket_img.save(ticket_filename)
        
        # Показываем билет в новом окне
        self.show_ticket_window(ticket_filename, ticket_info)
    
    def show_ticket_window(self, image_path, ticket_info):
        ticket_window = tk.Toplevel(self.root)
        ticket_window.title("Электронный билет")
        ticket_window.geometry("500x700")
        
        # Загружаем и отображаем изображение билета
        img = Image.open(image_path)
        img = img.resize((400, 600), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        
        label = tk.Label(ticket_window, image=photo)
        label.image = photo  # сохраняем ссылку
        label.pack(pady=10)
        
        # Кнопки
        btn_frame = tk.Frame(ticket_window)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Сохранить PNG", 
                 command=lambda: self.save_ticket_image(image_path)).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Закрыть", 
                 command=ticket_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def save_ticket_image(self, image_path):
        # В реальном приложении можно добавить выбор места сохранения
        messagebox.showinfo("Сохранено", f"Билет сохранен как {image_path}")
    
    def generate_revenue_report(self):
        """Генерация отчета о кассовых сборах в формате CSV с кодировкой UTF-16"""
        conn = sqlite3.connect('cinema.db')
        c = conn.cursor()
        
        # Получаем данные о продажах
        c.execute('''SELECT 
                  movies.title as movie_title,
                  COUNT(CASE WHEN bookings.status='paid' THEN 1 END) as tickets_sold,
                  SUM(movies.price) as total_revenue,
                  movies.hall as hall_number
                  FROM movies
                  LEFT JOIN bookings ON movies.id = bookings.movie_id
                  GROUP BY movies.title
                  ORDER BY total_revenue DESC''')
        
        report_data = c.fetchall()
        conn.close()
        
        # Определяем имя файла с текущей датой
        report_filename = f"revenue_report_{datetime.now().strftime('%Y-%m-%d')}.csv"
        
        try:
            # Создаем CSV файл с кодировкой UTF-16
            with open(report_filename, 'w', newline='', encoding='utf-16') as csvfile:
                writer = csv.writer(csvfile, delimiter='\t')
                
                # Заголовки
                writer.writerow([
                    'Название фильма',
                    'Количество проданных билетов',
                    'Общая выручка (руб)',
                    'Зал'
                ])
                
                # Данные
                for row in report_data:
                    writer.writerow([
                        row[0],  # Название фильма
                        row[1] if row[1] else 0,  # Билеты
                        f"{row[2]:.2f}" if row[2] else "0.00",  # Выручка
                        row[3]  # Зал
                    ])
                
                # Итоговая строка
                total_revenue = sum(row[2] if row[2] else 0 for row in report_data)
                writer.writerow([])
                writer.writerow(['ИТОГО:', '', f"{total_revenue:.2f}", ''])
            
            messagebox.showinfo("Успех", f"Отчет сохранен в файл: {report_filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать отчет: {str(e)}")
    
    def show_statistics(self):
        self.clear_window()
        tk.Label(self.root, text="Статистика и отчеты", font=("Arial", 18)).pack(pady=10)
        
        # Получение данных
        conn = sqlite3.connect('cinema.db')
        c = conn.cursor()
        
        # Статистика по фильмам
        c.execute('''SELECT movies.title, 
                  COUNT(CASE WHEN bookings.status='paid' THEN 1 END) as sold,
                  SUM(movies.price) as revenue
                  FROM movies
                  LEFT JOIN bookings ON movies.id = bookings.movie_id
                  GROUP BY movies.title''')
        
        movies = []
        sold_counts = []
        revenues = []
        
        for row in c.fetchall():
            movies.append(row[0])
            sold_counts.append(row[1] or 0)
            revenues.append(row[2] or 0)
        
        conn.close()
        
        # График популярности
        fig1, ax1 = plt.subplots(figsize=(8, 4))
        ax1.bar(movies, sold_counts, color='skyblue')
        ax1.set_title('Количество проданных билетов')
        ax1.set_ylabel('Билеты')
        ax1.tick_params(axis='x', rotation=45)
        
        canvas1 = FigureCanvasTkAgg(fig1, master=self.root)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # График выручки
        fig2, ax2 = plt.subplots(figsize=(8, 4))
        ax2.bar(movies, revenues, color='lightgreen')
        ax2.set_title('Кассовые сборы')
        ax2.set_ylabel('Рублей')
        ax2.tick_params(axis='x', rotation=45)
        
        canvas2 = FigureCanvasTkAgg(fig2, master=self.root)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Кнопка для генерации отчета
        tk.Button(self.root, text="Сгенерировать отчет", 
                 command=self.generate_revenue_report).pack(pady=5)
        
        tk.Button(self.root, text="Назад", command=self.show_main_screen).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = CinemaApp(root)
    root.mainloop()

import tkinter as tk
from tkinter import messagebox
import random
import sqlite3
from datetime import datetime

class MorseCodeTrainer:
    def __init__(self, master):
        self.master = master
        self.master.title("Обучение азбуке Морзе")
        
        # Инициализация данных
        self.morse_code = {
            'А': '.-', 'Б': '-...', 'В': '.--', 'Г': '--.', 'Д': '-..', 'Е': '.', 'Ё': '.',
            'Ж': '--..-', 'З': '--..', 'И': '..', 'Й': '.---', 'К': '-.-', 'Л': '.-..',
            'М': '--', 'Н': '-.', 'О': '---', 'П': '.--.', 'Р': '.-.', 'С': '...', 
            'Т': '-', 'У': '..-', 'Ф': '..-.', 'Х': '....', 'Ц': '-..-', 'Ч': '---.',
            'Ш': '----', 'Щ': '--.-', 'Ъ': '.--..', 'Ы': '-.--', 'Ь': '-..-', 'Э': '..-..',
            'Ю': '..--', 'Я': '.-.-'
        }
        self.mode = 'morse_to_letter'
        self.current_letter = ''
        self.correct_answers = 0
        self.total_questions = 0
        
        self.create_widgets()
        self.init_db()
        self.generate_question()

    def create_widgets(self):
        """Создание элементов интерфейса"""
        self.question_label = tk.Label(self.master, text="", font=("Arial", 16))
        self.question_label.pack(pady=20)

        self.entry = tk.Entry(self.master, font=("Arial", 16))
        self.entry.pack(pady=10)
        self.entry.bind('<Return>', lambda event: self.check_answer())

        self.check_button = tk.Button(self.master, text="Проверить", command=self.check_answer, font=("Arial", 16))
        self.check_button.pack(pady=10)

        self.mode_button = tk.Button(
            self.master, 
            text="Переключить на Буква -> Морзе", 
            command=self.toggle_mode,
            font=("Arial", 16)
        )
        self.mode_button.pack(pady=10)

        self.result_label = tk.Label(self.master, text="", font=("Arial", 16))
        self.result_label.pack(pady=10)

        self.stats_label = tk.Label(
            self.master, 
            text="Правильных ответов: 0/0", 
            font=("Arial", 14)
        )
        self.stats_label.pack(pady=10)

        stats_buttons_frame = tk.Frame(self.master)
        stats_buttons_frame.pack(pady=10)

        self.show_stats_button = tk.Button(
            stats_buttons_frame, 
            text="Показать статистику", 
            command=self.show_statistics, 
            font=("Arial", 12)
        )
        self.show_stats_button.pack(side=tk.LEFT, padx=5)

        self.reset_stats_button = tk.Button(
            stats_buttons_frame, 
            text="Сбросить статистику", 
            command=self.reset_statistics, 
            font=("Arial", 12)
        )
        self.reset_stats_button.pack(side=tk.LEFT, padx=5)

    def init_db(self):
        """Инициализация базы данных"""
        self.conn = sqlite3.connect('morse_trainer.db')
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                letter TEXT NOT NULL,
                morse_code TEXT NOT NULL,
                mode TEXT NOT NULL,
                is_correct INTEGER NOT NULL,
                timestamp TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now'))
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                correct_answers INTEGER DEFAULT 0,
                total_questions INTEGER DEFAULT 0,
                last_session TEXT
            )
        ''')
        
        self.cursor.execute('SELECT COUNT(*) FROM statistics')
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute('INSERT INTO statistics (correct_answers, total_questions) VALUES (0, 0)')
        
        self.conn.commit()
        self.load_statistics()

    def load_statistics(self):
        """Загрузка статистики из БД"""
        self.cursor.execute('SELECT correct_answers, total_questions FROM statistics WHERE id = 1')
        stats = self.cursor.fetchone()
        if stats:
            self.correct_answers, self.total_questions = stats
            self.update_stats_display()

    def save_statistics(self):
        """Сохранение статистики в БД"""
        self.cursor.execute('''
            UPDATE statistics 
            SET correct_answers = ?, total_questions = ?, last_session = ?
            WHERE id = 1
        ''', (self.correct_answers, self.total_questions, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        self.conn.commit()

    def save_answer(self, is_correct):
        """Сохранение ответа в БД"""
        self.cursor.execute('''
            INSERT INTO answers (letter, morse_code, mode, is_correct)
            VALUES (?, ?, ?, ?)
        ''', (self.current_letter, self.morse_code[self.current_letter], self.mode, 1 if is_correct else 0))
        self.conn.commit()

    def update_stats_display(self):
        """Обновление отображения статистики"""
        self.stats_label.config(text=f"Правильных ответов: {self.correct_answers}/{self.total_questions}")

    def reset_statistics(self):
        """Сброс всей статистики"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите сбросить всю статистику?"):
            self.cursor.execute('DELETE FROM answers')
            self.cursor.execute('UPDATE statistics SET correct_answers = 0, total_questions = 0')
            self.conn.commit()
            self.correct_answers = 0
            self.total_questions = 0
            self.update_stats_display()
            messagebox.showinfo("Сброс статистики", "Статистика успешно сброшена!")

    def show_statistics(self):
        """Отображение статистики в отдельном окне"""
        stats_window = tk.Toplevel(self.master)
        stats_window.title("Статистика ответов")
        
        # Получаем статистику по буквам
        self.cursor.execute('''
            SELECT letter, 
                   SUM(is_correct) as correct, 
                   COUNT(*) as total,
                   ROUND(SUM(is_correct) * 100.0 / COUNT(*), 1) as percent
            FROM answers
            GROUP BY letter
            ORDER BY percent ASC, total DESC
        ''')
        letters_stats = self.cursor.fetchall()
        
        # Получаем общую статистику
        self.cursor.execute('SELECT correct_answers, total_questions FROM statistics WHERE id = 1')
        total_correct, total_questions = self.cursor.fetchone()
        success_rate = round(total_correct * 100 / total_questions, 1) if total_questions > 0 else 0
        
        # Отображаем общую статистику
        tk.Label(stats_window, text="Общая статистика:", font=("Arial", 14, "bold")).pack(pady=5)
        tk.Label(
            stats_window, 
            text=f"Всего ответов: {total_questions}\nПравильных: {total_correct}\nУспешность: {success_rate}%",
            font=("Arial", 12)
        ).pack(pady=5)
        
        # Отображаем статистику по буквам
        tk.Label(stats_window, text="Статистика по буквам:", font=("Arial", 14, "bold")).pack(pady=5)
        
        for letter, correct, total, percent in letters_stats:
            tk.Label(
                stats_window, 
                text=f"{letter} ({self.morse_code[letter]}): {correct}/{total} ({percent}%)",
                font=("Arial", 12),
                fg="red" if percent < 50 else "black"
            ).pack(anchor='w', padx=20)

    def toggle_mode(self):
        """Переключение между режимами обучения"""
        self.mode = 'letter_to_morse' if self.mode == 'morse_to_letter' else 'morse_to_letter'
        self.mode_button.config(
            text="Переключить на " + 
            ("Морзе -> Буква" if self.mode == 'morse_to_letter' else "Буква -> Морзе")
        )
        self.generate_question()

    def check_answer(self):
        """Проверка ответа пользователя"""
        user_answer = self.entry.get().strip().upper()
        is_correct = False
        
        if self.mode == 'morse_to_letter':
            if user_answer == self.morse_code[self.current_letter]:
                self.result_label.config(text="Правильно!", fg="green")
                is_correct = True
            else:
                self.result_label.config(
                    text=f"Неправильно! Правильный ответ: {self.morse_code[self.current_letter]}", 
                    fg="red"
                )
        elif self.mode == 'letter_to_morse':
            if user_answer == self.current_letter:
                self.result_label.config(text="Правильно!", fg="green")
                is_correct = True
            else:
                self.result_label.config(
                    text=f"Неправильно! Правильный ответ: {self.current_letter}", 
                    fg="red"
                )
        
        self.total_questions += 1
        if is_correct:
            self.correct_answers += 1
        
        self.save_answer(is_correct)
        self.save_statistics()
        self.update_stats_display()
        self.entry.delete(0, tk.END)
        self.generate_question()

    def generate_question(self):
        """Генерация нового вопроса"""
        self.current_letter = random.choice(list(self.morse_code.keys()))
        if self.mode == 'morse_to_letter':
            self.question_label.config(text=f"Какой код Морзе для буквы '{self.current_letter}'?")
        elif self.mode == 'letter_to_morse':
            self.question_label.config(
                text=f"Какой буквå соответствует код Морзе '{self.morse_code[self.current_letter]}'?"
            )

    def __del__(self):
        """Закрытие соединения с БД при завершении"""
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    try:
        app = MorseCodeTrainer(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")
        root.destroy()

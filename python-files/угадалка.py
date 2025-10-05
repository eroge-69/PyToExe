import tkinter as tk
from tkinter import messagebox, ttk
import random

class NumberGuessingGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Угадай число")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Настройки игры
        self.min_range = 1
        self.max_range = 100
        self.max_attempts = 10
        self.secret_number = None
        self.attempts = 0
        self.game_mode = None
        
        # Стили
        self.setup_styles()
        
        # Создание интерфейса
        self.create_main_menu()
    
    def setup_styles(self):
        """Настройка стилей"""
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Subtitle.TLabel', font=('Arial', 12))
        style.configure('Big.TButton', font=('Arial', 12, 'bold'))
    
    def clear_frame(self):
        """Очистка текущего экрана"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def create_main_menu(self):
        """Главное меню"""
        self.clear_frame()
        
        # Заголовок
        title_label = ttk.Label(self.root, text="🎮 УГАДАЙ ЧИСЛО", style='Title.TLabel')
        title_label.pack(pady=20)
        
        # Подзаголовок
        subtitle_label = ttk.Label(self.root, text="Выберите режим игры:", style='Subtitle.TLabel')
        subtitle_label.pack(pady=10)
        
        # Кнопки режимов
        frame_buttons = ttk.Frame(self.root)
        frame_buttons.pack(pady=30)
        
        btn_player = ttk.Button(frame_buttons, text="🎯 Я угадываю", 
                               command=self.start_player_mode, style='Big.TButton')
        btn_player.pack(pady=10, fill='x')
        
        btn_computer = ttk.Button(frame_buttons, text="🤖 Компьютер угадывает", 
                                 command=self.start_computer_mode, style='Big.TButton')
        btn_computer.pack(pady=10, fill='x')
        
        btn_exit = ttk.Button(frame_buttons, text="🚪 Выход", 
                             command=self.root.quit, style='Big.TButton')
        btn_exit.pack(pady=10, fill='x')
    
    def start_player_mode(self):
        """Режим: игрок угадывает"""
        self.game_mode = "player"
        self.secret_number = random.randint(self.min_range, self.max_range)
        self.attempts = 0
        
        self.create_player_game_screen()
    
    def create_player_game_screen(self):
        """Экран игры для режима игрока"""
        self.clear_frame()
        
        # Заголовок
        title_label = ttk.Label(self.root, text="🎯 ВЫ УГАДЫВАЕТЕ", style='Title.TLabel')
        title_label.pack(pady=10)
        
        # Информация о игре
        info_label = ttk.Label(self.root, 
                              text=f"Я загадал число от {self.min_range} до {self.max_range}\n"
                                   f"У вас {self.max_attempts} попыток",
                              style='Subtitle.TLabel')
        info_label.pack(pady=5)
        
        # Счетчик попыток
        self.attempts_label = ttk.Label(self.root, 
                                       text=f"Попытка: {self.attempts}/{self.max_attempts}",
                                       font=('Arial', 10, 'bold'))
        self.attempts_label.pack(pady=5)
        
        # Поле ввода
        input_frame = ttk.Frame(self.root)
        input_frame.pack(pady=20)
        
        ttk.Label(input_frame, text="Ваше предположение:").pack()
        
        self.guess_entry = ttk.Entry(input_frame, font=('Arial', 14), width=10, justify='center')
        self.guess_entry.pack(pady=5)
        self.guess_entry.bind('<Return>', lambda e: self.check_guess())
        
        # Кнопка проверки
        btn_check = ttk.Button(input_frame, text="Проверить", 
                              command=self.check_guess, style='Big.TButton')
        btn_check.pack(pady=10)
        
        # Поле для подсказок
        self.hint_label = ttk.Label(self.root, text="", font=('Arial', 12, 'bold'), foreground='blue')
        self.hint_label.pack(pady=10)
        
        # История попыток
        self.history_frame = ttk.Frame(self.root)
        self.history_frame.pack(pady=10, fill='both', expand=True)
        
        ttk.Label(self.history_frame, text="История попыток:", font=('Arial', 10)).pack()
        
        self.history_text = tk.Text(self.history_frame, height=6, width=40, font=('Arial', 9))
        self.history_text.pack(pady=5)
        self.history_text.config(state=tk.DISABLED)
        
        # Кнопка возврата
        btn_back = ttk.Button(self.root, text="← Назад в меню", 
                             command=self.create_main_menu)
        btn_back.pack(pady=10)
    
    def check_guess(self):
        """Проверка предположения игрока"""
        try:
            guess = int(self.guess_entry.get())
            self.attempts += 1
            
            if guess < self.min_range or guess > self.max_range:
                messagebox.showwarning("Ошибка", 
                                     f"Введите число от {self.min_range} до {self.max_range}!")
                self.attempts -= 1
                return
            
            # Обновляем счетчик попыток
            self.attempts_label.config(text=f"Попытка: {self.attempts}/{self.max_attempts}")
            
            # Проверяем предположение
            if guess == self.secret_number:
                self.show_victory()
            elif guess < self.secret_number:
                self.hint_label.config(text="⬆️ Загаданное число БОЛЬШЕ", foreground='red')
            else:
                self.hint_label.config(text="⬇️ Загаданное число МЕНЬШЕ", foreground='red')
            
            # Добавляем в историю
            self.add_to_history(guess)
            
            # Очищаем поле ввода
            self.guess_entry.delete(0, tk.END)
            
            # Проверяем лимит попыток
            if self.attempts >= self.max_attempts and guess != self.secret_number:
                self.show_defeat()
                
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите целое число!")
    
    def add_to_history(self, guess):
        """Добавление попытки в историю"""
        self.history_text.config(state=tk.NORMAL)
        
        if guess == self.secret_number:
            status = "🎉 УГАДАЛ!"
            color = "green"
        elif guess < self.secret_number:
            status = "⬆️ МАЛО"
            color = "blue"
        else:
            status = "⬇️ МНОГО"
            color = "red"
        
        history_line = f"Попытка {self.attempts}: {guess} - {status}\n"
        
        self.history_text.insert(tk.END, history_line)
        self.history_text.tag_add(f"color_{self.attempts}", "end-2l", "end-1l")
        self.history_text.tag_config(f"color_{self.attempts}", foreground=color)
        
        self.history_text.see(tk.END)
        self.history_text.config(state=tk.DISABLED)
    
    def show_victory(self):
        """Показать победу"""
        messagebox.showinfo("ПОБЕДА!", 
                          f"🎉 Поздравляю! Вы угадали число {self.secret_number} за {self.attempts} попыток!")
        self.create_main_menu()
    
    def show_defeat(self):
        """Показать поражение"""
        messagebox.showinfo("ИГРА ОКОНЧЕНА", 
                          f"💔 Вы проиграли! Было загадано число: {self.secret_number}")
        self.create_main_menu()
    
    def start_computer_mode(self):
        """Режим: компьютер угадывает"""
        self.game_mode = "computer"
        self.computer_low = self.min_range
        self.computer_high = self.max_range
        self.computer_attempts = 0
        
        self.create_computer_game_screen()
    
    def create_computer_game_screen(self):
        """Экран игры для режима компьютера"""
        self.clear_frame()
        
        # Заголовок
        title_label = ttk.Label(self.root, text="🤖 КОМПЬЮТЕР УГАДЫВАЕТ", style='Title.TLabel')
        title_label.pack(pady=10)
        
        # Инструкция
        instruction_label = ttk.Label(self.root, 
                                     text="Загадайте число от 1 до 100\n"
                                          "Компьютер попробует его угадать",
                                     style='Subtitle.TLabel',
                                     justify='center')
        instruction_label.pack(pady=10)
        
        # Счетчик попыток компьютера
        self.comp_attempts_label = ttk.Label(self.root, 
                                           text=f"Попыток: {self.computer_attempts}",
                                           font=('Arial', 12, 'bold'))
        self.comp_attempts_label.pack(pady=5)
        
        # Предположение компьютера
        self.comp_guess_label = ttk.Label(self.root, 
                                         text="",
                                         font=('Arial', 24, 'bold'),
                                         foreground='purple')
        self.comp_guess_label.pack(pady=20)
        
        # Кнопки ответов
        buttons_frame = ttk.Frame(self.root)
        buttons_frame.pack(pady=20)
        
        btn_correct = ttk.Button(buttons_frame, text="✅ Правильно!", 
                               command=self.computer_correct, style='Big.TButton')
        btn_correct.grid(row=0, column=0, padx=10, pady=5)
        
        btn_higher = ttk.Button(buttons_frame, text="⬆️ Мое число БОЛЬШЕ", 
                               command=self.computer_higher, style='Big.TButton')
        btn_higher.grid(row=1, column=0, padx=10, pady=5)
        
        btn_lower = ttk.Button(buttons_frame, text="⬇️ Мое число МЕНЬШЕ", 
                              command=self.computer_lower, style='Big.TButton')
        btn_lower.grid(row=2, column=0, padx=10, pady=5)
        
        # Кнопка возврата
        btn_back = ttk.Button(self.root, text="← Назад в меню", 
                             command=self.create_main_menu)
        btn_back.pack(pady=10)
        
        # Делаем первое предположение
        self.make_computer_guess()
    
    def make_computer_guess(self):
        """Компьютер делает предположение"""
        self.computer_attempts += 1
        computer_guess = (self.computer_low + self.computer_high) // 2
        
        self.comp_attempts_label.config(text=f"Попыток: {self.computer_attempts}")
        self.comp_guess_label.config(text=str(computer_guess))
        
        self.current_computer_guess = computer_guess
    
    def computer_correct(self):
        """Игрок подтверждает, что компьютер угадал"""
        messagebox.showinfo("УСПЕХ!", 
                          f"🤖 Компьютер угадал ваше число {self.current_computer_guess} за {self.computer_attempts} попыток!")
        self.create_main_menu()
    
    def computer_higher(self):
        """Игрок говорит, что число больше"""
        self.computer_low = self.current_computer_guess + 1
        if self.computer_low > self.computer_high:
            messagebox.showerror("Ошибка", "Вы где-то ошиблись с подсказками!")
            self.create_main_menu()
        else:
            self.make_computer_guess()
    
    def computer_lower(self):
        """Игрок говорит, что число меньше"""
        self.computer_high = self.current_computer_guess - 1
        if self.computer_high < self.computer_low:
            messagebox.showerror("Ошибка", "Вы где-то ошиблись с подсказками!")
            self.create_main_menu()
        else:
            self.make_computer_guess()

def main():
    root = tk.Tk()
    app = NumberGuessingGameGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
    
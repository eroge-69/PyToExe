import tkinter as tk
from tkinter import messagebox
import time
import random

def fake_hack():
    root = tk.Tk()
    root.withdraw()  # Скрываем основное окно
    
    # Заставка "взлома"
    messagebox.showwarning("ВНИМАНИЕ!", "Обнаружена вирусная активность!")
    time.sleep(1)
    
    # Рандомные "проценты взлома"
    for i in range(5):
        percent = random.randint(10, 90)
        messagebox.showinfo("Взлом системы...", f"Загрузка вируса... {percent}%")
        time.sleep(0.5)
    
    # Финальное сообщение
    messagebox.showerror("ВЗЛОМ УСПЕШЕН!", "Ха-ха-ха! Ваш компьютер взломан!\n(Шутка, это просто программа 😊)")
    
    # Дополнительно: можно добавить мигающее окно
    for _ in range(3):
        root = tk.Tk()
        root.geometry("300x100")
        root.title("⚠️ ВНИМАНИЕ! ⚠️")
        label = tk.Label(root, text="ВАС ВЗЛОМАЛИ!", font=("Arial", 20), fg="red")
        label.pack()
        root.after(1000, root.destroy)  # Закрыть через 1 секунду
        root.mainloop()
        time.sleep(0.3)

if __name__ == "__main__":
    fake_hack()
import tkinter as tk
import random
import time
from tkinter import messagebox
import threading

def create_error_window():
    error_window = tk.Tk()
    error_window.title("ОШИБКА")
    error_window.attributes('-topmost', True)
    error_window.geometry("400x200+" + str(random.randint(0, 1000)) + "+" + str(random.randint(0, 600)))
    
    label = tk.Label(error_window, text="ВАШ КОМПЬЮТЕР ВЗЛОМАН", fg="red", font=("Arial", 16, "bold"))
    label.pack(pady=20)
    
    error_text = "Ошибка #" + str(random.randint(1000, 9999)) + "\n"
    error_text += random.choice([
        "Обнаружена критическая уязвимость!",
        "Доступ к файлам запрещен!",
        "Вирус активирован!",
        "Шифрование данных...",
        "Системный сбой!",
        "Несанкционированный доступ!",
        "Файлы повреждены!",
        "Ошибка памяти!",
        "Заражение подтверждено!",
        "Данные передаются хакерам!",
    ])
    
    error_label = tk.Label(error_window, text=error_text, font=("Arial", 12))
    error_label.pack(pady=10)
    
    error_window.after(random.randint(3000, 8000), error_window.destroy)
    error_window.mainloop()

def fake_antivirus_scan():
    root = tk.Tk()
    root.title("Антивирусная проверка")
    root.geometry("500x300")
    root.attributes('-topmost', True)
    
    label = tk.Label(root, text="Сканирование на вирусы...", font=("Arial", 14))
    label.pack(pady=20)
    
    progress = tk.Label(root, text="0% завершено", font=("Arial", 12))
    progress.pack()
    
    for i in range(1, 101):
        time.sleep(0.1)
        progress.config(text=f"{i}% завершено")
        root.update()
        if i == 100:
            messagebox.showerror("Результат", "Обнаружено 15 вирусов! Система скомпрометирована!")
            root.destroy()

if __name__ == "__main__":
    for _ in range(15):
        threading.Thread(target=create_error_window).start()
        time.sleep(0.5)
    threading.Thread(target=fake_antivirus_scan).start()
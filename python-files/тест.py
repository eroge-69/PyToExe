import tkinter as tk
import os
import time
from threading import Thread


def shutdown_computer(seconds):
   
    time.sleep(seconds)
    os.system("shutdown /s /t 1")  # Для Windows
    # Для Linux: os.system("shutdown -h now")


def create_warning_window():
    
    window = tk.Tk()
    window.title("⚠️ МУ ХА ХА ХА ХА! ⚠️")
    window.geometry("400x200")
    window.configure(bg='black')

    # Делаем окно поверх всех
    window.attributes('-topmost', True)

    # Текст предупреждения
    label = tk.Label(
        window,
        text="\n🚨 прости!\n\nТЕБЯ ВЗЛОМАЛИ\n МОЛСИЬ \n\n",
        font=("Arial", 14, "bold"),
        fg="red",
        bg="black",
        justify="center"
    )
    label.pack(pady=20)

    # Счетчик времени
    time_label = tk.Label(
        window,
        text="Осталось: 60 секунд",
        font=("Arial", 12),
        fg="yellow",
        bg="black"
    )
    time_label.pack()

    # Кнопка отмены
    def cancel_shutdown():
        os.system("shutdown /a")  # Отмена выключения
        window.destroy()


    # Обновление счетчика
    def update_timer(seconds_left):
        if seconds_left > 0:
            time_label.config(text=f"Осталось: {seconds_left} секунд")
            window.after(1000, update_timer, seconds_left - 1)

    update_timer(60)
    window.mainloop()


# Запуск
if __name__ == "__main__":
    # Запускаем выключение через 60 секунд в отдельном потоке
    shutdown_thread = Thread(target=shutdown_computer, args=(60,))
    shutdown_thread.daemon = True
    shutdown_thread.start()

    # Показываем окно предупреждения
    create_warning_window()
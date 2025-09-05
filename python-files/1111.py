autoimport subprocess
import time
import pyautogui
import tkinter as tk
from tkinter import messagebox


def run_powershell_command():
    try:
        # Запуск PowerShell от имени администратора
        subprocess.Popen([
            "powershell",
            "Start-Process",
            "powershell",
            "-ArgumentList",
            "'-NoExit -Command irm https://get.activated.win | iex'",
            "-Verb",
            "RunAs"
        ])

        # Ждем, пока окно PowerShell станет активным
        time.sleep(5)

        # Ждем 30 секунд и вводим '1'
        time.sleep(40)
        pyautogui.write('1')
        pyautogui.press('enter')

        # Ждем 20 секунд и вводим еще раз '1'
        time.sleep(70)
        pyautogui.write('1')
        pyautogui.press('enter')

    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")


# Создаем графический интерфейс
root = tk.Tk()
root.title("Активатор")
root.geometry("300x100")

activate_button = tk.Button(
    root,
    text="Активировать",
    command=run_powershell_command,
    font=("Arial", 14)
)
activate_button.pack(pady=20)

root.mainloop()
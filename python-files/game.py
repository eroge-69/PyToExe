
import tkinter as tk
from tkinter import messagebox
import time

def show_message():
    root = tk.Tk()
    root.withdraw()  # Прячем основное окно

messagebox.askyesnocancel("VirusAlert!", f"Привет,я албанский вирус, но к сожалению, из-за слабого развития технологий в моей стране я не могу навредить вашему комьпютеру. Пожалуйста будьте добры, удалите один из важных файлов самостоятельно, а затем перешлите другим пользователям. Большое спасибо, за сотрудничество. С наилучшими пожеланиями, Албанский вирус ")

if __name__ == "__main__":
    show_message()
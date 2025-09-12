import win32print
import win32ui
from tkinter import *
from tkinter import ttk


def print():
        
    # Укажите здесь точное имя вашего принтера или используйте текущий принтер по умолчанию:
    printer_name = win32print.GetDefaultPrinter()
    # printer_name = "Proton PPT-4206"  # <- можно указать вручную, если нужно

    # Создаём контекст печати
    hprinter = win32print.OpenPrinter(printer_name)
    printer_info = win32print.GetPrinter(hprinter, 2)

    pdc = win32ui.CreateDC()
    pdc.CreatePrinterDC(printer_name)

    # Начинаем печать
    pdc.StartDoc("Python Print Job")
    pdc.StartPage()

    # Печатаем текст — координаты: (x=100, y=100)
    pdc.TextOut(60, 60, "Привет, Proton PPT-4206!")

    pdc.EndPage()
    pdc.EndDoc()
    pdc.DeleteDC()



root = Tk()     # создаем корневой объект - окно
root.title("Tiket print")     # устанавливаем заголовок окна
root.geometry("640x480")    # устанавливаем размеры окна
 
root.resizable(False, False)

btn1 = ttk.Button(text="Поиск")
btn1.place(x=50, y=400)

btn2 = ttk.Button(text="Печать")
btn2.place(x=150, y=400)

btn3 = ttk.Button(text="Внести даныне")
btn3.place(x=250, y=400)

btn3 = ttk.Button(text="Очистить")
btn3.place(x=360, y=400)

root.mainloop()
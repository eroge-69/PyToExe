import tkinter as tk
from tkinter import messagebox

# Создаем главное окно (оно будет скрыто)
root = tk.Tk()
root.withdraw()

# Текст для уведомления
text = """1242869862951551076 - еблан
702197413301059624 - wernello
1151909850465456168 - okkyyy
1162697282504896593 - хуесос обход

https://www.youtube.com/watch?v=2EnUIMCD9l4
abcdf55 - обход дс
kswxww - мейн дс"""

# Показываем сообщение  
messagebox.showinfo("Слить и забанить ", text)

# Освобождаем ресурсы Tkinter
root.destroy()
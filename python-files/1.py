import tkinter as tk


root = tk.Tk()


root.title('Привет!')


label = tk.Label(root, text='Привет, Коля!', font=('Arial', 16))
label.pack(pady=20)


root.mainloop()
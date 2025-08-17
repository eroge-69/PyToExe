import tkinter as tk

root = tk.Tk()
root.title("Мое приложение")
root.geometry("300x200")

label = tk.Label(root, text="Привет, Windows!")
label.pack()

button = tk.Button(root, text="Закрыть", command=root.quit)
button.pack()

root.mainloop()
import tkinter as tk

def on_button_click():
    label.config(text="Привет, мир!")

app = tk.Tk()
app.title("Простое приложение")

label = tk.Label(app, text="Нажмите кнопку")
label.pack(pady=10)

button = tk.Button(app, text="Нажми меня", command=on_button_click)
button.pack(pady=10)

app.mainloop()
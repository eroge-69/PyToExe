import customtkinter
import PIL
from PIL import Image, ImageTk
import random
import os

# Устанавливаем тему (опционально)
customtkinter.set_appearance_mode("dark")  # режим: "dark" или "light"
customtkinter.set_default_color_theme("blue")

# Создаём окно
win = customtkinter.CTk()
win.title("Пример окна с customtkinter")
win.geometry("400x300")

value = 0  # начальное значение

def animate():
    global value
    if value <= 100:
        progressbar.set(value / 100)  # значение от 0.0 до 1.0
        value += 1
        win.after(20, animate)
    else:
        value = 0
        win.after(20, animate)

# Добавляем кнопку
def on_button_click():
    print("Кнопка нажата!")

button = customtkinter.CTkButton(win, text="Нажми меня", command=on_button_click, corner_radius=0)
button.pack(pady=20)

# button.configure()
# число = random.randint(1, 10)
# число = random.choice([1, 2, 3])

image = Image.open('icon.ico')
image = image.resize((64, 64))
photo = ImageTk.PhotoImage(image)
label = customtkinter.CTkLabel(win, image=photo, text="")
label.pack(pady=10)

scrollable = customtkinter.CTkScrollableFrame(win, width=280, height=250)
scrollable.pack(pady=10)

scale = customtkinter.CTkSlider(win, from_=0, to=1, orientation="vertical")
scale.pack(pady=20)

progressbar = customtkinter.CTkProgressBar(win, orientation="vertical", progress_color="red", fg_color="gray90", border_color="black", border_width=2)
# progressbar.set(0.5)  # от 0 до 1
progressbar.pack(pady=20, padx=20, fill="y", expand=True)

customtkinter.CTkButton(scrollable, text=f"Кнопка").pack(pady=2)
customtkinter.CTkButton(scrollable, text=f"Кнопка").pack(pady=2)
customtkinter.CTkButton(scrollable, text=f"Кнопка").pack(pady=2)
customtkinter.CTkButton(scrollable, text=f"Кнопка").pack(pady=2)
customtkinter.CTkButton(scrollable, text=f"Кнопка").pack(pady=2)
customtkinter.CTkButton(scrollable, text=f"Кнопка").pack(pady=2)
customtkinter.CTkButton(scrollable, text=f"Кнопка").pack(pady=2)
customtkinter.CTkButton(scrollable, text=f"Кнопка").pack(pady=2)

frame1 = customtkinter.CTkScrollableFrame(win, width=100, height=100, fg_color="red")
frame1.pack()

frame2 = customtkinter.CTkScrollableFrame(win, width=50, height=50, fg_color="yellow")
frame2.pack()

frame3 = customtkinter.CTkScrollableFrame(win, width=25, height=25, fg_color="blue")
frame3.pack()

animate()
win.mainloop()

# name = entry.get()
# entry.delete(0, 4)
# entry.insert(0, "Иванов")
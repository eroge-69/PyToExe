from tkinter import *
from tkinter import ttk, filedialog
import random
import time
from PIL import Image, ImageTk

def ap():
    target = random.randint(0, 100)
    progress['maximum'] = 100
    
    for i in range(target + 1):
        progress['value'] = i
        label.config(text=f"Прогресс: {i}/{target}")
        root.update()
        time.sleep(0.03)
    
    label.config(text=f"Результат: тело заряжено свагой на {target}% из 100")

def upload_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
    if file_path: 
        img = Image.open(file_path)
        img = img.resize((250, 250))  # err
        img = ImageTk.PhotoImage(img)
        image_label.config(image=img)
        image_label.image = img 

root = Tk()
root.title("СВАГОМЕТР")
root.geometry("800x600")  
root.config(bd=20, bg='#a290e8')

lm = Label(text='Свагометр',
           font=('Comic Sans MS', 24, 'bold'))

lm.config(bd=20, bg='#6d35e5')
lm.pack()

progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress.pack(pady=20)

label = Label(root, text="Прогресс: 0/0")
label.pack()

button = Button(root, text="Измерить", command=ap)
button.pack(pady=10)

upload_button = Button(root, text="Выбрать изображение", command=upload_image)
upload_button.pack(pady=10)

image_label = Label(root)
image_label.pack(pady=20)

root.mainloop()


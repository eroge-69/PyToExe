import tkinter as tk
from tkinter import messagebox
import random
import time
import threading
from PIL import Image, ImageTk

CORRECT_KEY = "39bVX0="

def generate_random_list():
    return [random.randint(10000000, 999999999) for _ in range(3)]

def show_software_screen(root, canvas, bg_img):
    canvas.delete("all")
    canvas.create_image(0, 0, anchor="nw", image=bg_img)
    canvas.create_text(250, 50, text="CONNECTED TO SOFTWARE", fill="lime", font=("Courier", 16, "bold"))
    
    for i in range(5):
        numbers = generate_random_list()
        canvas.create_text(250, 100 + i * 40, text=str(numbers), fill="white", font=("Courier", 14))

def connecting_screen(root, canvas, bg_img):
    canvas.delete("all")
    canvas.create_image(0, 0, anchor="nw", image=bg_img)
    canvas.create_text(250, 200, text="Connecting to Server...", fill="white", font=("Courier", 16))
    
    def delayed_transition():
        time.sleep(2.5)
        show_software_screen(root, canvas, bg_img)
    
    threading.Thread(target=delayed_transition).start()

def verify_key(entry, root, canvas, bg_img):
    key = entry.get()
    if key == CORRECT_KEY:
        connecting_screen(root, canvas, bg_img)
    else:
        messagebox.showerror("Access Denied", "Invalid Key")

def main():
    root = tk.Tk()
    root.title("BRAIN_BOX.EXE")
    root.geometry("500x400")
    root.resizable(False, False)

    bg_image = Image.open("checkerboard.png").resize((500, 400))
    bg_img = ImageTk.PhotoImage(bg_image)

    canvas = tk.Canvas(root, width=500, height=400)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, anchor="nw", image=bg_img)
    canvas.create_text(250, 100, text="ENTER ACCESS KEY", fill="white", font=("Courier", 16, "bold"))

    entry = tk.Entry(root, font=("Courier", 14), justify="center")
    entry.place(x=150, y=150, width=200)

    btn = tk.Button(root, text="UNLOCK", command=lambda: verify_key(entry, root, canvas, bg_img), font=("Courier", 12, "bold"))
    btn.place(x=210, y=200)

    root.mainloop()

if __name__ == "__main__":
    main()

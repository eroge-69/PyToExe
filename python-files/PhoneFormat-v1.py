
import re
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
import base64
import io

logo_base64 = 'iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAABp0lEQVR4nO3c0W6DMBBE0aX//8/0oUJ1LEgDtb0z9j3vaSzuLqhqRQQAAAAAAAAAAAAAAJjavu979hla+Mo+AF5NEeTYjhm2ZIogM7EPUm+F+5bYB5mNdZCrbXDeEusgM7IN8tcWuG6JbZBZWQb5dPodt8QyyMzsgtyderctsQsyO6sgT6fdaUusgqzAJsh/p9xlS2yCrMIiSKvpdtgSiyArkQ/SeqrVt0Q+yGqkg/SaZuUtkQ6yItkgvadYdUtkg6xKMsio6VXcEskgK5MLMnpq1bZELsjqpIJkTavSlkgFgVCQ7CnN/v6DTBD8kAiiMp0K55AIgl/pQRSmspR9nvQgeJUaJHsar2Seiw0RkxZEdTsO6ucDAAAAAAAAAAAAAHS3ZR+gVP8de9u2bucb+V138F8nYggihiBipILU9/FRb3JQeX5EiAWBQRDeBpRs9O1D6XYVIRjkDG+US3Y2tT1egqm2HRFiv6nXriLcuZAtfsZIkocqvduMdxf16eeyyR6s1PLerxwjQvQZUmt1EdVjRJhsSOnJtjiEONgc9IzrcwIAgB6+AZSK58ev8Ei+AAAAAElFTkSuQmCC'

def decode_logo(base64_string):
    image_data = base64.b64decode(base64_string)
    return Image.open(io.BytesIO(image_data))

def format_numbers():
    text = input_text.get("1.0", tk.END)
    numbers = re.findall(r'\+7\d{10}|8\d{10}|(?<!\d)7\d{9}(?!\d)', text)
    formatted = set()
    for num in numbers:
        digits = re.sub(r'\D', '', num)
        if digits.startswith("8"):
            digits = "7" + digits[1:]
        if digits.startswith("7"):
            digits = digits[1:]
        if len(digits) == 10:
            formatted.add(digits)
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, "\n".join(formatted))

root = tk.Tk()
root.title("Phone Number Formatter")
root.configure(bg="#003366")
root.geometry("600x500")

logo_img = decode_logo(logo_base64)
logo_photo = ImageTk.PhotoImage(logo_img.resize((50, 50)))
logo_label = tk.Label(root, image=logo_photo, bg="#003366")
logo_label.pack(pady=10)

input_label = tk.Label(root, text="Вставьте текст:", fg="white", bg="#003366")
input_label.pack()
input_text = ScrolledText(root, height=8, bg="#002244", fg="white", insertbackground='white')
input_text.pack(fill="both", padx=10, pady=5)

start_button = tk.Button(root, text="Старт", command=format_numbers, bg="#0055aa", fg="white")
start_button.pack(pady=10)

output_label = tk.Label(root, text="Результат:", fg="white", bg="#003366")
output_label.pack()
output_text = ScrolledText(root, height=8, bg="#002244", fg="white")
output_text.pack(fill="both", padx=10, pady=5)

root.mainloop()

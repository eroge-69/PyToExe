import tkinter as tk
from tkinter import ttk, Toplevel
import requests

API_TOKEN = "101560278129264" 
BASE_URL = f"https://superheroapi.com/api/{API_TOKEN}/search/"

def search_hero():
    name = entry.get()
    if not name:
        return
    response = requests.get(BASE_URL + name)
    data = response.json()

    
    for widget in result_frame.winfo_children():
        widget.destroy()

    if data.get("response") == "success":
        hero = data["results"][0]

        top = Toplevel(root)
        top.title("Інформація про героя")
        top.geometry("400x300")
        top.configure(bg="#1a1a2e")

        ttk.Label(top, text=f"Ім'я: {hero['name']}", font=('Arial', 14)).pack(pady=5)
        ttk.Label(top, text=f"Реальне ім'я: {hero['biography']['full-name']}").pack()
        ttk.Label(top, text=f"Всесвіт: {hero['biography']['publisher']}").pack()
        ttk.Label(top, text=f"Стать: {hero['appearance']['gender']}").pack()
        ttk.Label(top, text=f"Раса: {hero['appearance']['race']}").pack()
    else:
        ttk.Label(result_frame, text="Героя не знайдено.", foreground="red").pack()


root = tk.Tk()
root.title("Пошук супергероїв")
root.geometry("400x200")
root.configure(bg="#0f3460")

frame = ttk.Frame(root, padding=20)
frame.pack(expand=True)

ttk.Label(frame, text="Введіть ім'я супергероя:").pack()
entry = ttk.Entry(frame, width=30)
entry.pack(pady=5)

button = ttk.Button(frame, text="Пошук", command=search_hero)
button.pack(pady=10)

result_frame = ttk.Frame(root, padding=10)
result_frame.pack()

root.mainloop()

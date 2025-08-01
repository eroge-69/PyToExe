import os
import random
import tkinter as tk
from tkinter import filedialog, messagebox

# ==== BRANDS AND CATEGORIES ====
brands = ["Toyota", "Honda", "Nissan", "Ford", "BMW", "Mercedes", "Audi", "Subaru", "Mazda", "Chevrolet"]
categories = ["sports", "sedans", "coupes", "motorcycles", "compacts", "suvs", "vans", "muscle", "classics", "offroad"]

price_min = 1000
price_max = 2500

def generate_lua(folder_path):
    output_path = os.path.join(folder_path, "output.lua")
    with open(output_path, "w") as f:
        f.write("return {\n")
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(".ytd"):
                    model = os.path.splitext(file)[0]
                    name = model.replace("_", " ")
                    brand = random.choice(brands)
                    category = random.choice(categories)
                    price = random.randint(price_min, price_max)
                    f.write(f"    {{ model = '{model}', name = '{name}', brand = '{brand}', price = {price}, category = '{category}', type = 'automobile', shop = 'pdm' }},\n")
        f.write("}\n")
    messagebox.showinfo("✅ Done", f"Lua file generated at:\n{output_path}")

def browse_folder():
    folder = filedialog.askdirectory()
    if folder:
        generate_lua(folder)

# ==== GUI ====
app = tk.Tk()
app.title("YTD to Lua Generator - by Otaku Sensei")
app.geometry("500x300")
app.resizable(False, False)

header = tk.Label(app, text="🚗 YTD to Lua Vehicle Generator", font=("Segoe UI", 14, "bold"))
header.pack(pady=10)

desc = tk.Label(app, text="Generates random Lua table entries from .ytd vehicle files
Version: 1.0", font=("Segoe UI", 10))
desc.pack()

browse_btn = tk.Button(app, text="📁 Select Folder to Scan", command=browse_folder, font=("Segoe UI", 11), bg="#0078D7", fg="white", padx=10, pady=5)
browse_btn.pack(pady=30)

footer = tk.Label(app, text="Created by Otaku Sensei | Discord: otakusensei6969\nGitHub: github.com/0takusensei/Qbcore-YTD-to-Lua-Vehicle-Lua-Generator", font=("Segoe UI", 8), fg="gray", justify="center")
footer.pack(side="bottom", pady=10)

app.mainloop()

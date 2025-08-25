import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os

FILE = "recipes.json"

def load_recipes():
    if os.path.exists(FILE):
        with open(FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_recipes():
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(recipes, f, indent=4, ensure_ascii=False)

def add_recipe():
    name = simpledialog.askstring("Новый рецепт", "Введите название рецепта:")
    if not name:
        return
    ingredients = {}
    while True:
        ing = simpledialog.askstring("Ингредиенты", "Введите ингредиент (или оставьте пустым для завершения):")
        if not ing:
            break
        grams = simpledialog.askfloat("Количество", f"Сколько грамм {ing}?")
        if grams:
            ingredients[ing] = grams
    if ingredients:
        recipes[name] = ingredients
        save_recipes()
        update_recipe_list()
        messagebox.showinfo("Сохранено", f"Рецепт '{name}' добавлен!")

def update_recipe_list():
    recipe_list.delete(0, tk.END)
    for name in recipes.keys():
        recipe_list.insert(tk.END, name)

def show_recipe(event=None):
    selection = recipe_list.curselection()
    if not selection:
        return
    name = recipe_list.get(selection[0])
    ingredients = recipes[name]
    text.delete(1.0, tk.END)
    text.insert(tk.END, f"📖 {name}\n\n")
    for ing, g in ingredients.items():
        text.insert(tk.END, f" - {ing}: {g} г\n")

def scale_recipe():
    selection = recipe_list.curselection()
    if not selection:
        messagebox.showwarning("Ошибка", "Выберите рецепт!")
        return
    name = recipe_list.get(selection[0])
    ingredients = recipes[name]

    base_ing = simpledialog.askstring("Выбор ингредиента", "Введите главный ингредиент:")
    if base_ing not in ingredients:
        messagebox.showerror("Ошибка", "Такого ингредиента нет в рецепте!")
        return

    have = simpledialog.askfloat("Сколько есть", f"Сколько у вас {base_ing} (г)?")
    if not have:
        return

    factor = have / ingredients[base_ing]

    text.delete(1.0, tk.END)
    text.insert(tk.END, f"🔄 Пересчитанный рецепт: {name}\n\n")
    for ing, g in ingredients.items():
        text.insert(tk.END, f" - {ing}: {round(g * factor, 2)} г\n")

# --- GUI ---
root = tk.Tk()
root.title("📖 Книга рецептов")
root.geometry("600x400")

# Список рецептов
frame_left = tk.Frame(root)
frame_left.pack(side="left", fill="y")

recipe_list = tk.Listbox(frame_left, width=25)
recipe_list.pack(fill="y", expand=True, padx=5, pady=5)
recipe_list.bind("<<ListboxSelect>>", show_recipe)

btn_add = tk.Button(frame_left, text="➕ Добавить рецепт", command=add_recipe)
btn_add.pack(fill="x", padx=5, pady=2)

btn_scale = tk.Button(frame_left, text="🔄 Пересчитать", command=scale_recipe)
btn_scale.pack(fill="x", padx=5, pady=2)

# Текстовое поле справа
frame_right = tk.Frame(root)
frame_right.pack(side="right", fill="both", expand=True)

text = tk.Text(frame_right, wrap="word", font=("Arial", 12))
text.pack(fill="both", expand=True, padx=5, pady=5)

# Загружаем рецепты
recipes = load_recipes()
update_recipe_list()

root.mainloop()

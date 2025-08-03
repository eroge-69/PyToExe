import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import json
import os
import shutil

# הגדרות תיקיות וקבצים
DATA_DIR = "user_data"
IMAGES_DIR = os.path.join(DATA_DIR, "images")
DATA_FILE = os.path.join(DATA_DIR, "data.json")

os.makedirs(IMAGES_DIR, exist_ok=True)

# טעינת דאטה
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        database = json.load(f)
else:
    database = []

def save_database():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(database, f, indent=2, ensure_ascii=False)

def choose_image():
    path = filedialog.askopenfilename(filetypes=[("תמונות", "*.jpg *.jpeg *.png")])
    if path:
        image_path_var.set(path)

def add_entry():
    name = name_entry.get().strip()
    desc = desc_entry.get().strip()
    img_path = image_path_var.get()
    if not name or not img_path:
        messagebox.showerror("שגיאה", "חובה למלא שם ולבחור תמונה.")
        return
    try:
        filename = os.path.basename(img_path)
        dest_path = os.path.join(IMAGES_DIR, filename)
        shutil.copy(img_path, dest_path)
        entry = {
            "name": name,
            "description": desc,
            "image": dest_path
        }
        database.append(entry)
        save_database()
        messagebox.showinfo("הצלחה", "המשתמש נשמר בהצלחה!")
        name_entry.delete(0, tk.END)
        desc_entry.delete(0, tk.END)
        image_path_var.set("")
    except Exception as e:
        messagebox.showerror("שגיאה", f"שגיאה בשמירה: {e}")

def search_by_name():
    search_name = search_name_entry.get().strip().lower()
    for entry in database:
        if entry["name"].lower() == search_name:
            display_result(entry)
            return
    clear_result()
    result_label.config(text="לא נמצא משתמש עם השם הזה.")

def search_by_image():
    path = filedialog.askopenfilename(filetypes=[("תמונות", "*.jpg *.jpeg *.png")])
    if not path:
        return
    for entry in database:
        try:
            if os.path.samefile(entry["image"], path):
                display_result(entry)
                return
        except FileNotFoundError:
            continue
    clear_result()
    result_label.config(text="לא נמצא משתמש עם תמונה זו.")

def display_result(entry):
    result_label.config(text=f"שם: {entry['name']}\nתיאור: {entry['description']}")
    try:
        img = Image.open(entry["image"])
        img.thumbnail((150, 150))
        img_tk = ImageTk.PhotoImage(img)
        result_image_label.image = img_tk  # שמירת הפניה למניעת garbage collection
        result_image_label.config(image=img_tk)
    except Exception:
        result_image_label.config(image="")

def clear_result():
    result_label.config(text="")
    result_image_label.config(image="")

# יצירת חלון ראשי פשוט ויעיל
root = tk.Tk()
root.title("מאגר משתמשים")
root.geometry("450x550")

notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill='both')

# טאב להוספת משתמש
tab_add = tk.Frame(notebook)
notebook.add(tab_add, text="הוספת משתמש")

tk.Label(tab_add, text="שם:", font=("Arial", 12)).pack(pady=5)
name_entry = tk.Entry(tab_add, font=("Arial", 12), width=40)
name_entry.pack()

tk.Label(tab_add, text="תיאור (אופציונלי):", font=("Arial", 12)).pack(pady=5)
desc_entry = tk.Entry(tab_add, font=("Arial", 12), width=40)
desc_entry.pack()

tk.Label(tab_add, text="בחר תמונה:", font=("Arial", 12)).pack(pady=5)
image_path_var = tk.StringVar()
tk.Entry(tab_add, textvariable=image_path_var, font=("Arial", 10), width=40, state="readonly").pack()
tk.Button(tab_add, text="בחר קובץ", command=choose_image).pack(pady=5)

tk.Button(tab_add, text="שמור", bg="lightgreen", font=("Arial", 12), command=add_entry).pack(pady=15)

# טאב לחיפוש משתמשים
tab_search = tk.Frame(notebook)
notebook.add(tab_search, text="חיפוש משתמש")

tk.Label(tab_search, text="חיפוש לפי שם:", font=("Arial", 12)).pack(pady=5)
search_name_entry = tk.Entry(tab_search, font=("Arial", 12), width=40)
search_name_entry.pack()

tk.Button(tab_search, text="חפש שם", bg="lightblue", font=("Arial", 12), command=search_by_name).pack(pady=5)

tk.Label(tab_search, text="או חיפוש לפי תמונה:", font=("Arial", 12)).pack(pady=10)
tk.Button(tab_search, text="בחר תמונה לחיפוש", bg="lightblue", font=("Arial", 12), command=search_by_image).pack(pady=5)

result_label = tk.Label(tab_search, text="", font=("Arial", 11))
result_label.pack(pady=15)

result_image_label = tk.Label(tab_search)
result_image_label.pack()

# השורה החשובה שתשאיר את החלון פתוח בלי סגירה פתאומית:
root.mainloop()

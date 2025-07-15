import pandas as pd
import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox

# Δημιουργούμε global μεταβλητές
selected_excel = ""
selected_folder1 = ""
selected_folder2 = ""

def browse_excel():
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
    excel_entry.delete(0, tk.END)
    excel_entry.insert(0, file_path)

def browse_folder1():
    folder_path = filedialog.askdirectory()
    folder1_entry.delete(0, tk.END)
    folder1_entry.insert(0, folder_path)

def browse_folder2():
    folder_path = filedialog.askdirectory()
    folder2_entry.delete(0, tk.END)
    folder2_entry.insert(0, folder_path)

def get_available_name(folder_path, base_name, extension):
    new_name = f"{base_name}{extension}"
    new_path = os.path.join(folder_path, new_name)
    index = 1

    while os.path.exists(new_path):
        new_name = f"{base_name}_{index}{extension}"
        new_path = os.path.join(folder_path, new_name)
        index += 1

    return new_path

def submit():
    global selected_excel, selected_folder1, selected_folder2

    excel = excel_entry.get()
    folder1 = folder1_entry.get()
    folder2 = folder2_entry.get()

    if not excel or not folder1 or not folder2:
        messagebox.showwarning("Προσοχή", "Συμπλήρωσε όλα τα πεδία.")
        return

    selected_excel = excel
    selected_folder1 = folder1
    selected_folder2 = folder2

    # Ανάγνωση Excel
    try:
        df = pd.read_excel(selected_excel)
        table = df.values
        identity = table[:, 0]
        name = table[:, 1]
        print("Excel:", df)
    except Exception as e:
        messagebox.showerror("Σφάλμα", f"Πρόβλημα στην ανάγνωση του Excel:\n{e}")
        return

    # --- Βήμα 1: Βρες όλα τα αρχεία από folder1 ---
    all_files = []
    for root_dir, dirs, files in os.walk(selected_folder1):
        for file in files:
            file_path = os.path.join(root_dir, file)
            all_files.append(file_path)

    print("📁 Βρέθηκαν αρχεία:")
    for f in all_files:
        print(f)

    # --- Βήμα 2: Μετονομασία αρχείων ---
    new_paths = []

    for file in all_files:
        for i, ids in enumerate(identity):
            if ids.lower() in file.lower() and file.lower().endswith(".png"):
                new_name = f"{ids} {name[i]}"
                new_path = get_available_name(os.path.dirname(file), new_name, ".png")
                try:
                    os.rename(file, new_path)
                    new_paths.append(new_path)
                    print(f"✅ Μετονομάστηκε: {file} -> {new_path}")
                except Exception as e:
                    print(f"❌ Σφάλμα μετονομασίας: {e}")

    # --- Βήμα 3: Βρες τους υποφακέλους από folder2 ---
    folder_paths = []
    for root_dir, dirs, files in os.walk(selected_folder2):
        for dir_name in dirs:
            folder_paths.append(os.path.join(root_dir, dir_name))

    # --- Βήμα 4: Αντιγραφή αρχείων στους σωστούς φακέλους ---
    for source_file in new_paths:
        for i, ids in enumerate(identity):
            if ids.lower() in source_file.lower():
                for destination_folder in folder_paths:
                    if ids.lower() in destination_folder.lower():
                        dest_file = os.path.join(destination_folder, os.path.basename(source_file))
                        if not os.path.exists(dest_file):
                            shutil.copy2(source_file, dest_file)
                            print(f"📁 Αντιγράφηκε: {source_file} -> {dest_file}")
                        else:
                            new_dest = get_available_name(destination_folder, os.path.splitext(os.path.basename(source_file))[0], ".png")
                            shutil.copy2(source_file, new_dest)
                            print(f"⚠️ Υπήρχε ήδη. Αντιγράφηκε ως: {new_dest}")

    messagebox.showinfo("Ολοκληρώθηκε", "Η διαδικασία ολοκληρώθηκε επιτυχώς!")

# ----------------- GUI -----------------
root = tk.Tk()
root.title("Επιλογή Excel και Φακέλων")
root.geometry("700x300")

tk.Label(root, text="Επιλογή Excel αρχείου:").pack()
excel_entry = tk.Entry(root, width=80)
excel_entry.pack(pady=2)
tk.Button(root, text="Αναζήτηση Excel", command=browse_excel).pack(pady=2)

tk.Label(root, text="Επιλογή πρώτου φακέλου (πηγή):").pack()
folder1_entry = tk.Entry(root, width=80)
folder1_entry.pack(pady=2)
tk.Button(root, text="Αναζήτηση Φακέλου 1", command=browse_folder1).pack(pady=2)

tk.Label(root, text="Επιλογή δεύτερου φακέλου (προορισμός):").pack()
folder2_entry = tk.Entry(root, width=80)
folder2_entry.pack(pady=2)
tk.Button(root, text="Αναζήτηση Φακέλου 2", command=browse_folder2).pack(pady=2)

tk.Button(root, text="Υποβολή", command=submit, bg="green", fg="white").pack(pady=10)

root.mainloop()
               
            

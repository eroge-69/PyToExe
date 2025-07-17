
import tkinter as tk
from tkinter import messagebox, ttk
import os
import subprocess
import sys

def open_file():
    category = category_var.get()
    search_type = search_type_var.get()
    query = entry.get().strip()

    if not query:
        messagebox.showwarning("Προσοχή", "Παρακαλώ πληκτρολογήστε αριθμό ή ημερομηνία.")
        return

    folder = "κανονικές" if category == "Κανονικές" else "εξαρμωμένες"
    possible_extensions = ['.pdf', '.jpg', '.png']
    found = False

    try:
        files = os.listdir(folder)
    except FileNotFoundError:
        messagebox.showerror("Σφάλμα", f"Ο φάκελος '{folder}' δεν βρέθηκε.")
        return

    for file in files:
        filepath = os.path.join(folder, file)
        if not os.path.isfile(filepath):
            continue

        name, ext = os.path.splitext(file)
        if ext.lower() not in possible_extensions:
            continue

        if search_type == "Αριθμός" and query in name:
            found = True
        elif search_type == "Ημερομηνία" and name.startswith(query):
            found = True

        if found:
            try:
                if sys.platform.startswith('darwin'):
                    subprocess.call(('open', filepath))
                elif os.name == 'nt':
                    os.startfile(filepath)
                elif os.name == 'posix':
                    subprocess.call(('xdg-open', filepath))
                return
            except Exception as e:
                messagebox.showerror("Σφάλμα", f"Δεν ήταν δυνατή η εκκίνηση του αρχείου: {e}")
                return

    messagebox.showinfo("Αποτυχία", "Η πιστοποίηση δεν βρέθηκε.")

def exit_program():
    root.destroy()

root = tk.Tk()
root.title("duroskal")
root.geometry("450x300")

tk.Label(root, text="Κατηγορία Πιστοποίησης:", font=("Arial", 11)).pack(pady=5)
category_var = tk.StringVar()
category_menu = ttk.Combobox(root, textvariable=category_var, state="readonly")
category_menu['values'] = ("Κανονικές", "Εξαρμωμένες")
category_menu.current(0)
category_menu.pack(pady=5)

tk.Label(root, text="Είδος Αναζήτησης:", font=("Arial", 11)).pack(pady=5)
search_type_var = tk.StringVar()
search_menu = ttk.Combobox(root, textvariable=search_type_var, state="readonly")
search_menu['values'] = ("Αριθμός", "Ημερομηνία")
search_menu.current(0)
search_menu.pack(pady=5)

tk.Label(root, text="Αναζήτηση:", font=("Arial", 11)).pack(pady=5)
entry = tk.Entry(root, font=("Arial", 14), justify='center')
entry.pack(pady=5)

search_button = tk.Button(root, text="Αναζήτηση", command=open_file, width=20)
search_button.pack(pady=10)

exit_button = tk.Button(root, text="Έξοδος", command=exit_program, width=20)
exit_button.pack()

root.mainloop()

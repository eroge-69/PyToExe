import os
import re
from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime

if not os.path.exists("timologia"):
    os.makedirs("timologia")

if not os.path.exists("ylika.txt"):
    with open("ylika.txt", "w", encoding="utf-8") as f:
        f.write("")

window = Tk()
window.geometry("900x650")
window.title("ΠΡΟΓΡΑΜΜΑ ΑΠΟΘΗΚΕΥΣΗΣ ΤΙΜΟΛΟΓΙΩΝ")

notebook = ttk.Notebook(window)
notebook.pack(expand=True, fill=BOTH)

# ----------------------- TAB 1 -----------------------
tab1 = Frame(notebook)
notebook.add(tab1, text="Καταχώρηση")

Label(tab1, text="Ονοματεπώνυμο:", font=('Arial', 12)).pack(pady=5)
entry_name = Entry(tab1, width=50)
entry_name.pack()

Label(tab1, text="Κινητό Τηλέφωνο:", font=('Arial', 12)).pack(pady=5)
entry_phone = Entry(tab1, width=50)
entry_phone.pack()

Label(tab1, text="Ημερομηνία (π.χ. 27-06-2025):", font=('Arial', 12)).pack(pady=5)
entry_date = Entry(tab1, width=50)
entry_date.pack()

Label(tab1, text="Υλικά προς καταχώρηση", font=('Arial', 12, 'bold')).pack(pady=10)
ylika_frame = Frame(tab1)
ylika_frame.pack(pady=5)

Label(ylika_frame, text="Όνομα Υλικού:").grid(row=0, column=0, padx=5)
entry_yliko = Entry(ylika_frame, width=20)
entry_yliko.grid(row=0, column=1)

Label(ylika_frame, text="Τιμή (€):").grid(row=0, column=2, padx=5)
entry_timi = Entry(ylika_frame, width=10)
entry_timi.grid(row=0, column=3)

Label(ylika_frame, text="Ποσότητα:").grid(row=0, column=4, padx=5)
entry_posotita = Entry(ylika_frame, width=5)
entry_posotita.insert(0, "1")
entry_posotita.grid(row=0, column=5)

ylika_listbox = Listbox(tab1, width=90, height=6)
ylika_listbox.pack(pady=10)

ylika_data = []

saved_ylika = {}
def load_saved_ylika():
    global saved_ylika
    saved_ylika = {}
    if os.path.exists("ylika.txt"):
        with open("ylika.txt", "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) == 2:
                    saved_ylika[parts[0]] = float(parts[1])
load_saved_ylika()

def save_ylika_file():
    with open("ylika.txt", "w", encoding="utf-8") as f:
        for name, price in saved_ylika.items():
            f.write(f"{name},{price}\n")

Label(tab1, text="Αποθηκευμένα Υλικά:", font=('Arial', 11, 'bold')).pack(pady=(10, 2))
ylika_combobox = ttk.Combobox(tab1, values=list(saved_ylika.keys()), width=50)
ylika_combobox.pack()

def autofill_from_saved(event):
    selected = ylika_combobox.get()
    if selected in saved_ylika:
        entry_yliko.delete(0, END)
        entry_yliko.insert(0, selected)
        entry_timi.delete(0, END)
        entry_timi.insert(0, str(saved_ylika[selected]))
        entry_posotita.delete(0, END)
        entry_posotita.insert(0, "1")

ylika_combobox.bind("<<ComboboxSelected>>", autofill_from_saved)

def update_total_label():
    total = sum(q * t for _, t, q in ylika_data)
    label_total.config(text=f"Τρέχον Σύνολο: {total:.2f}€")

def add_yliko():
    name = entry_yliko.get().strip()
    timi = entry_timi.get().strip()
    posotita = entry_posotita.get().strip()
    if not name or not timi or not posotita:
        messagebox.showwarning("Σφάλμα", "Συμπληρώστε όλα τα πεδία.")
        return
    try:
        timi_float = float(timi)
        posotita_int = int(posotita)
    except ValueError:
        messagebox.showerror("Σφάλμα", "Η τιμή και η ποσότητα πρέπει να είναι αριθμοί.")
        return
    yliko_string = f"{name} | Τιμή: {timi_float}€ x {posotita_int}"
    ylika_listbox.insert(END, yliko_string)
    ylika_data.append((name, timi_float, posotita_int))
    saved_ylika[name] = timi_float
    save_ylika_file()
    ylika_combobox["values"] = list(saved_ylika.keys())
    entry_yliko.delete(0, END)
    entry_timi.delete(0, END)
    entry_posotita.delete(0, END)
    entry_posotita.insert(0, "1")
    update_total_label()

Button(tab1, text="Προσθήκη Υλικού", command=add_yliko).pack(pady=5)

label_total = Label(tab1, text="Τρέχον Σύνολο: 0.00€", font=('Arial', 11, 'bold'))
label_total.pack(pady=5)

def save_data():
    name = entry_name.get().strip()
    phone = entry_phone.get().strip()
    date = entry_date.get().strip()
    if not name or not date:
        messagebox.showwarning("Σφάλμα", "Συμπληρώστε όλα τα πεδία.")
        return
    try:
        datetime.strptime(date, "%d-%m-%Y")
    except ValueError:
        messagebox.showerror("Σφάλμα", "Η ημερομηνία δεν είναι έγκυρη.")
        return
    safe_name = re.sub(r'\W+', '_', name.lower())
    filename = f"timologia/{safe_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    txt_filename = filename + ".txt"
    with open(txt_filename, "w", encoding='utf-8') as f:
        f.write(f"Ονοματεπώνυμο: {name}\n")
        f.write(f"Κινητό Τηλέφωνο: {phone}\n")
        f.write(f"Ημερομηνία: {date}\n")
        f.write("Υλικά:\n")
        total = 0
        for yliko_name, timi, posotita in ylika_data:
            subtotal = posotita * timi
            total += subtotal
            f.write(f"- {yliko_name}: {posotita} x {timi}€ = {subtotal:.2f}€\n")
        f.write(f"Σύνολο υλικών: {total:.2f}€\n")
    entry_name.delete(0, END)
    entry_phone.delete(0, END)
    entry_date.delete(0, END)
    ylika_listbox.delete(0, END)
    ylika_data.clear()
    update_total_label()
    update = Listbox()

Button(tab1, text="Αποθήκευση Τιμολογίου", command=save_data, font=('Arial', 12)).pack(pady=20)

# ----------------------- TAB 2 -----------------------
tab2 = Frame(notebook)
notebook.add(tab2, text="Διαχείριση")

left_frame = Frame(tab2)
left_frame.pack(side=LEFT, fill=Y, padx=10, pady=10)

right_frame = Frame(tab2)
right_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)

Label(left_frame, text="Αποθηκευμένα Τιμολόγια:", font=('Arial', 12, 'bold')).pack(pady=5)

entry_search = Entry(left_frame, width=25)
entry_search.pack(pady=5)

def search_timologia():
    query = entry_search.get().strip().lower()
    timologia_listbox.delete(0, END)
    for file in os.listdir("timologia"):
        if file.endswith(".txt"):
            filepath = os.path.join("timologia", file)
            with open(filepath, "r", encoding="utf-8") as f:
                first_line = f.readline().strip().lower()
                if query in first_line:
                    timologia_listbox.insert(END, file)

Button(left_frame, text="Αναζήτηση", command=search_timologia).pack(pady=5)

timologia_listbox = Listbox(left_frame, width=30, height=20)
timologia_listbox.pack(pady=5)

selected_filename = None

info_frame = Frame(right_frame)
info_frame.pack(fill=X)

entry_edit_name = Entry(info_frame, width=30)
entry_edit_name.grid(row=0, column=0, padx=5, pady=2)
entry_edit_phone = Entry(info_frame, width=20)
entry_edit_phone.grid(row=0, column=1, padx=5, pady=2)
entry_edit_date = Entry(info_frame, width=20)
entry_edit_date.grid(row=0, column=2, padx=5, pady=2)

ylika_tree = ttk.Treeview(right_frame, columns=("onoma", "posotita", "timi", "subtotal"), show="headings")
ylika_tree.heading("onoma", text="Υλικό")
ylika_tree.heading("posotita", text="Ποσότητα")
ylika_tree.heading("timi", text="Τιμή (€)")
ylika_tree.heading("subtotal", text="Σύνολο (€)")
ylika_tree.pack(fill=BOTH, expand=True, pady=10)

label_total = Label(right_frame, text="Σύνολο Υλικών: 0.00€", font=('Arial', 11, 'bold'))
label_total.pack(pady=5)

entry_tree_yliko = Entry(right_frame, width=40, fg="grey")
entry_tree_yliko.insert(0, "Υλικό")
entry_tree_yliko.pack()

entry_tree_posotita = Entry(right_frame, width=40, fg="grey")
entry_tree_posotita.insert(0, "Ποσότητα")
entry_tree_posotita.pack()

entry_tree_timi = Entry(right_frame, width=40, fg="grey")
entry_tree_timi.insert(0, "Τιμή (€)")
entry_tree_timi.pack()

def load_timologio(event):
    global selected_filename
    selection = timologia_listbox.curselection()
    if not selection:
        return
    filename = timologia_listbox.get(selection[0])
    selected_filename = filename
    with open(f"timologia/{filename}", "r", encoding="utf-8") as f:
        lines = f.readlines()
    entry_edit_name.delete(0, END)
    entry_edit_phone.delete(0, END)
    entry_edit_date.delete(0, END)
    entry_edit_name.insert(0, lines[0].split(":", 1)[1].strip())
    entry_edit_phone.insert(0, lines[1].split(":", 1)[1].strip())
    entry_edit_date.insert(0, lines[2].split(":", 1)[1].strip())
    ylika_tree.delete(*ylika_tree.get_children())
    reading_ylika = False
    total = 0
    for line in lines:
        if line.strip() == "Υλικά:":
            reading_ylika = True
            continue
        if reading_ylika:
            if line.strip().startswith("-"):
                match = re.match(r"- (.*?): (\d+) x ([\d.]+)€ = ([\d.]+)€", line)
                if match:
                    yliko = match.group(1)
                    posotita = match.group(2)
                    timi = match.group(3)
                    subtotal = match.group(4)
                    ylika_tree.insert("", END, values=(yliko, posotita, timi, subtotal))
            elif line.startswith("Σύνολο υλικών"):
                total_match = re.search(r"([\d.]+)€", line)
                if total_match:
                    label_total.config(text=f"Σύνολο Υλικών: {total_match.group(1)}€")

def save_edits():
    if not selected_filename:
        return
    name = entry_edit_name.get().strip()
    phone = entry_edit_phone.get().strip()
    date = entry_edit_date.get().strip()
    try:
        datetime.strptime(date, "%d-%m-%Y")
    except ValueError:
        messagebox.showerror("Σφάλμα", "Η ημερομηνία δεν είναι έγκυρη.")
        return
    lines = [
        f"Ονοματεπώνυμο: {name}\n",
        f"Κινητό Τηλέφωνο: {phone}\n",
        f"Ημερομηνία: {date}\n",
        "Υλικά:\n"
    ]
    total = 0
    for child in ylika_tree.get_children():
        values = ylika_tree.item(child)["values"]
        name, posotita, timi, subtotal = values
        lines.append(f"- {name}: {posotita} x {timi}€ = {float(posotita)*float(timi):.2f}€\n")
        total += float(posotita)*float(timi)
    lines.append(f"Σύνολο υλικών: {total:.2f}€\n")
    with open(f"timologia/{selected_filename}", "w", encoding="utf-8") as f:
        f.writelines(lines)
    update = Listbox()
    label_total.config(text=f"Σύνολο Υλικών: {total:.2f}€")

Button(right_frame, text="Αποθήκευση Αλλαγών", command=save_edits, fg="blue").pack(pady=5)

def add_to_tree():
    name = entry_tree_yliko.get()
    try:
        posotita = int(entry_tree_posotita.get())
        timi = float(entry_tree_timi.get())
        subtotal = posotita * timi
        ylika_tree.insert("", END, values=(name, posotita, timi, subtotal))
    except ValueError:
        messagebox.showerror("Σφάλμα", "Λάθος ποσότητα ή τιμή")

Button(right_frame, text="Προσθήκη Υλικού", command=add_to_tree).pack(pady=2)

Button(left_frame, text="Ανανέωση Λίστας", command=search_timologia).pack(pady=5)
timologia_listbox.bind("<<ListboxSelect>>", load_timologio)

def delete_timologio():
    global selected_filename
    if selected_filename:
        filepath = f"timologia/{selected_filename}"
        if os.path.exists(filepath):
            os.remove(filepath)
            selected_filename = None
            update = Listbox()
            ylika_tree.delete(*ylika_tree.get_children())
            entry_edit_name.delete(0, END)
            entry_edit_phone.delete(0, END)
            entry_edit_date.delete(0, END)
            label_total.config(text="Σύνολο Υλικών: 0.00€")

Button(left_frame, text="Διαγραφή Τιμολογίου", command=delete_timologio, fg="red").pack(pady=5)

update = Listbox()

window.mainloop()

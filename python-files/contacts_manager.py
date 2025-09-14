import sqlite3
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import vobject

DB_FILE = "contacts.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    phone TEXT,
                    email TEXT)''')
    conn.commit()
    conn.close()

def import_vcf(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        vcf_data = f.read()
    for vcard in vobject.readComponents(vcf_data):
        name = vcard.fn.value if hasattr(vcard, "fn") else ""
        phone = vcard.tel.value if hasattr(vcard, "tel") else ""
        email = vcard.email.value if hasattr(vcard, "email") else ""
        save_contact(name, phone, email)

def save_contact(name, phone, email):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO contacts (name, phone, email) VALUES (?, ?, ?)", (name, phone, email))
    conn.commit()
    conn.close()

def update_contact(contact_id, name, phone, email):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE contacts SET name=?, phone=?, email=? WHERE id=?", (name, phone, email, contact_id))
    conn.commit()
    conn.close()

def delete_contact(contact_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM contacts WHERE id=?", (contact_id,))
    conn.commit()
    conn.close()

def export_vcf(file_path):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT name, phone, email FROM contacts")
    contacts = c.fetchall()
    conn.close()

    with open(file_path, "w", encoding="utf-8") as f:
        for name, phone, email in contacts:
            vcard = vobject.vCard()
            vcard.add("fn").value = name
            if phone:
                tel = vcard.add("tel")
                tel.value = phone
            if email:
                em = vcard.add("email")
                em.value = email
            f.write(vcard.serialize())

# ---------- GUI funkcie ----------
def import_file():
    file_path = filedialog.askopenfilename(filetypes=[("VCF files", "*.vcf")])
    if file_path:
        import_vcf(file_path)
        refresh_list()

def export_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".vcf")
    if file_path:
        export_vcf(file_path)
        messagebox.showinfo("Hotovo", "Kontakty boli exportované.")

def refresh_list(search_term=""):
    listbox.delete(0, tk.END)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    if search_term:
        query = f"%{search_term}%"
        c.execute("SELECT id, name, phone, email FROM contacts WHERE name LIKE ? OR phone LIKE ? OR email LIKE ?", (query, query, query))
    else:
        c.execute("SELECT id, name, phone, email FROM contacts")
    rows = c.fetchall()
    conn.close()

    for row in rows:
        listbox.insert(tk.END, f"{row[0]} | {row[1]} | {row[2]} | {row[3]}")

def add_contact():
    name = simpledialog.askstring("Meno", "Zadaj meno:")
    phone = simpledialog.askstring("Telefón", "Zadaj telefón:")
    email = simpledialog.askstring("Email", "Zadaj email:")
    if name:
        save_contact(name, phone or "", email or "")
        refresh_list()

def edit_contact():
    selection = listbox.curselection()
    if not selection:
        messagebox.showwarning("Upozornenie", "Najprv vyber kontakt.")
        return

    contact_data = listbox.get(selection[0]).split(" | ")
    contact_id = int(contact_data[0])

    new_name = simpledialog.askstring("Meno", "Uprav meno:", initialvalue=contact_data[1])
    new_phone = simpledialog.askstring("Telefón", "Uprav telefón:", initialvalue=contact_data[2])
    new_email = simpledialog.askstring("Email", "Uprav email:", initialvalue=contact_data[3])

    update_contact(contact_id, new_name, new_phone, new_email)
    refresh_list()

def delete_selected():
    selection = listbox.curselection()
    if not selection:
        messagebox.showwarning("Upozornenie", "Najprv vyber kontakt.")
        return

    contact_data = listbox.get(selection[0]).split(" | ")
    contact_id = int(contact_data[0])

    if messagebox.askyesno("Potvrdenie", f"Chceš vymazať {contact_data[1]}?"):
        delete_contact(contact_id)
        refresh_list()

def search_contacts():
    term = search_entry.get().strip()
    refresh_list(term)

# ---------- Spustenie ----------
init_db()

root = tk.Tk()
root.title("Správca kontaktov (VCF)")

# Vyhľadávanie
search_frame = tk.Frame(root)
search_frame.pack(pady=5)
tk.Label(search_frame, text="Hľadaj:").pack(side=tk.LEFT, padx=5)
search_entry = tk.Entry(search_frame, width=30)
search_entry.pack(side=tk.LEFT, padx=5)
tk.Button(search_frame, text="Hľadaj", command=search_contacts).pack(side=tk.LEFT, padx=5)
tk.Button(search_frame, text="Obnoviť", command=refresh_list).pack(side=tk.LEFT, padx=5)

# Zoznam
frame = tk.Frame(root)
frame.pack(pady=10)
listbox = tk.Listbox(frame, width=80, height=15)
listbox.pack(side=tk.LEFT, fill=tk.BOTH)
scrollbar = tk.Scrollbar(frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=listbox.yview)

# Ovládacie tlačidlá
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="Pridať", command=add_contact).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="Upraviť", command=edit_contact).grid(row=0, column=1, padx=5)
tk.Button(btn_frame, text="Vymazať", command=delete_selected).grid(row=0, column=2, padx=5)
tk.Button(btn_frame, text="Import VCF", command=import_file).grid(row=0, column=3, padx=5)
tk.Button(btn_frame, text="Export VCF", command=export_file).grid(row=0, column=4, padx=5)

refresh_list()

root.mainloop()

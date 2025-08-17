import tkinter as tk
from tkinter import ttk, Toplevel, messagebox
import random
import csv

admin_password = "admin123"
friends_list = []

# Freunde registrieren
def register_friend():
    def add_friend():
        fn_name = entry_fn_name.get()
        real_name = entry_real_name.get()
        if fn_name and real_name:
            friends_list.append((fn_name, real_name))
            update_friend_list()
            entry_fn_name.delete(0, tk.END)
            entry_real_name.delete(0, tk.END)
        else:
            messagebox.showwarning("Fehler", "Bitte beide Namen eingeben.")

    def update_friend_list():
        listbox.delete(0, tk.END)
        for fn, real in friends_list:
            listbox.insert(tk.END, f"{fn} ({real})")

    def delete_friend():
        selected = listbox.curselection()
        if selected:
            del friends_list[selected[0]]
            update_friend_list()
        else:
            messagebox.showwarning("Fehler", "Bitte einen Freund auswählen.")

    def edit_friend():
        selected = listbox.curselection()
        if selected:
            index = selected[0]
            fn_name = entry_fn_name.get()
            real_name = entry_real_name.get()
            if fn_name and real_name:
                friends_list[index] = (fn_name, real_name)
                update_friend_list()
                entry_fn_name.delete(0, tk.END)
                entry_real_name.delete(0, tk.END)
            else:
                messagebox.showwarning("Fehler", "Bitte beide Namen eingeben.")
        else:
            messagebox.showwarning("Fehler", "Bitte einen Freund auswählen.")

    def download_friends():
        try:
            with open("fortnite_friends.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Fortnite Name", "Echter Name"])
                writer.writerows(friends_list)
            messagebox.showinfo("Download", "Freunde wurden erfolgreich als fortnite_friends.csv gespeichert.")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern: {e}")

    friend_window = Toplevel(root)
    friend_window.title("👥 Freunde registrieren")
    friend_window.geometry("350x500")
    friend_window.configure(bg="#2c2f33")

    ttk.Label(friend_window, text="Fortnite Name:", font=("Helvetica", 11)).pack(pady=5)
    entry_fn_name = ttk.Entry(friend_window, width=30)
    entry_fn_name.pack(pady=5)

    ttk.Label(friend_window, text="Echter Name:", font=("Helvetica", 11)).pack(pady=5)
    entry_real_name = ttk.Entry(friend_window, width=30)
    entry_real_name.pack(pady=5)

    ttk.Button(friend_window, text="➕ Freund hinzufügen", command=add_friend).pack(pady=5)
    ttk.Button(friend_window, text="✏️ Freund bearbeiten", command=edit_friend).pack(pady=5)
    ttk.Button(friend_window, text="❌ Freund löschen", command=delete_friend).pack(pady=5)

    ttk.Label(friend_window, text="Freunde-Liste:", font=("Helvetica", 11, "bold")).pack(pady=5)
    listbox = tk.Listbox(friend_window, width=40)
    listbox.pack(pady=5)

    ttk.Button(friend_window, text="📥 Freunde herunterladen", command=download_friends).pack(pady=10)

    update_friend_list()

# Der Rest deines Skripts bleibt unverändert (Account Übersicht, Admin Panel etc.)


# Account Übersicht
def show_account_overview():
    name = entry_name.get()
    level = entry_level.get()
    vbucks = entry_vbucks.get()
    has_battlepass = var_battlepass.get()

    if not name or not level or not vbucks:
        messagebox.showwarning("Fehlende Eingabe", "Bitte alle Felder ausfüllen.")
        return

    try:
        level = int(level)
        vbucks = int(vbucks)
    except ValueError:
        messagebox.showerror("Ungültige Eingabe", "Level und V-Bucks müssen Zahlen sein.")
        return

    overview_window = Toplevel(root)
    overview_window.title("🗞 Fortnite Account Übersicht")
    overview_window.geometry("400x250")
    overview_window.configure(bg="#2c2f33")

    ttk.Label(overview_window, text="🔹 Fortnite Account Übersicht", font=("Helvetica", 13, "bold")).pack(pady=10)
    ttk.Label(overview_window, text=f"👤 Name: {name}", font=("Helvetica", 11)).pack(pady=5)
    ttk.Label(overview_window, text=f"📈 Level: {level}", font=("Helvetica", 11)).pack(pady=5)
    ttk.Label(overview_window, text=f"💰 V-Bucks: {vbucks}", font=("Helvetica", 11)).pack(pady=5)
    ttk.Label(overview_window, text=f"🎟️ Battle Pass: {'Ja' if has_battlepass else 'Nein'}", font=("Helvetica", 11)).pack(pady=5)

# Admin Panel
def open_admin_panel():
    def check_password():
        if password_entry.get() == admin_password:
            password_window.destroy()
            show_admin_panel()
        else:
            messagebox.showerror("Fehler", "Falsches Passwort!")

    password_window = Toplevel(root)
    password_window.title("🔐 Admin Login")
    password_window.geometry("300x150")
    password_window.configure(bg="#2c2f33")

    ttk.Label(password_window, text="🔑 Passwort eingeben:", font=("Helvetica", 11)).pack(pady=10)
    password_entry = ttk.Entry(password_window, show="*", width=25)
    password_entry.pack(pady=5)
    ttk.Button(password_window, text="Login", command=check_password).pack(pady=10)

def show_admin_panel():
    admin_window = Toplevel(root)
    admin_window.title("🔧 Admin Panel")
    admin_window.geometry("300x250")
    admin_window.configure(bg="#1e1f29")

    ttk.Label(admin_window, text="🔐 Admin Zugriff", font=("Helvetica", 12, "bold")).pack(pady=10)
    ttk.Label(admin_window, text="Spezielle Inhalte und Einstellungen", font=("Helvetica", 10)).pack(pady=5)

    ttk.Button(admin_window, text="🔑 Passwort ändern", command=change_password).pack(pady=5)
    ttk.Button(admin_window, text="🎁 Fake V-Bucks Generator", command=fake_vbucks_generator).pack(pady=5)

def change_password():
    def update_password():
        new_pw = new_password_entry.get()
        if new_pw:
            global admin_password
            admin_password = new_pw
            messagebox.showinfo("Erfolg", "Passwort wurde erfolgreich geändert.")
            pw_window.destroy()
        else:
            messagebox.showwarning("Fehler", "Bitte ein neues Passwort eingeben.")

    pw_window = Toplevel(root)
    pw_window.title("🔑 Passwort ändern")
    pw_window.geometry("300x150")
    pw_window.configure(bg="#2c2f33")

    ttk.Label(pw_window, text="Neues Passwort eingeben:", font=("Helvetica", 11)).pack(pady=10)
    new_password_entry = ttk.Entry(pw_window, show="*", width=25)
    new_password_entry.pack(pady=5)
    ttk.Button(pw_window, text="Speichern", command=update_password).pack(pady=10)

def fake_vbucks_generator():
    fake_code = "VB-" + "-".join(["".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=4)) for _ in range(3)])
    messagebox.showinfo("🎁 V-Bucks Generator", f"Dein (nicht echter) V-Bucks-Code:\n\n{fake_code}\n\nHinweis: Nur zur Unterhaltung!")

# Hauptfenster
root = tk.Tk()
root.title("🎮 Fortnite Profil App")
root.geometry("400x550")
root.configure(bg="#2c2f33")

style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", background="#2c2f33", foreground="white", font=("Helvetica", 11))
style.configure("TButton", background="#7289da", foreground="white", font=("Helvetica", 11, "bold"))
style.configure("TCheckbutton", background="#2c2f33", foreground="white", font=("Helvetica", 11))

# Buttons
ttk.Button(root, text="🔧 Admin Panel", command=open_admin_panel).pack(pady=5)
ttk.Button(root, text="👥 Freunde registrieren", command=register_friend).pack(pady=5)

frame = ttk.Frame(root, padding=20)
frame.pack(expand=True)

ttk.Label(frame, text="Fortnite Name:").grid(row=0, column=0, sticky="e", pady=5)
entry_name = ttk.Entry(frame, width=30)
entry_name.grid(row=0, column=1, pady=5)

ttk.Label(frame, text="Level:").grid(row=1, column=0, sticky="e", pady=5)
entry_level = ttk.Entry(frame, width=30)
entry_level.grid(row=1, column=1, pady=5)

ttk.Label(frame, text="V-Bucks:").grid(row=2, column=0, sticky="e", pady=5)
entry_vbucks = ttk.Entry(frame, width=30)
entry_vbucks.grid(row=2, column=1, pady=5)

var_battlepass = tk.BooleanVar()
ttk.Checkbutton(frame, text="Battle Pass vorhanden", variable=var_battlepass).grid(row=3, columnspan=2, pady=10)

ttk.Button(frame, text="Account Übersicht anzeigen", command=show_account_overview).grid(row=4, columnspan=2, pady=15)

root.mainloop()
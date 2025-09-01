# main.py
import tkinter as tk
from tkinter import ttk, messagebox
from auth import AuthManager
from admin import open_admin_panel
from video_manager import open_user_panel
from update_system import UpdateSystem

update_sys = UpdateSystem()
if update_sys.is_updating():
    import tkinter as tk
    root = tk.Tk()
    root.title("Clipo - Aggiornamento")
    tk.Label(root, text="Ci dispiace, c'è un aggiornamento in corso.\nRiprova più tardi.").pack(padx=20, pady=20)
    root.mainloop()
    exit()

# LANG CONFIG
LANGUAGES = {
    "ITA": {
        "login": "Accedi",
        "register": "Registrati",
        "email": "Email",
        "password": "Password",
        "repeat_password": "Ripeti Password",
        "dob": "Data di nascita (YYYY-MM-DD)",
        "human_test": "Quanto fa 3 + 5?",
        "image": "Carica Immagine (opzionale)",
        "submit": "Invia",
        "not_human": "Test fallito. Sei un robot?",
        "wrong_owner_pass": "Password proprietario errata.",
        "language_select": "Seleziona la lingua",
        "owner_pass": "Password proprietario"
    },
    "ENG": {
        "login": "Login",
        "register": "Register",
        "email": "Email",
        "password": "Password",
        "repeat_password": "Repeat Password",
        "dob": "Date of Birth (YYYY-MM-DD)",
        "human_test": "What's 3 + 5?",
        "image": "Upload Image (optional)",
        "submit": "Submit",
        "not_human": "Failed the human test. Are you a robot?",
        "wrong_owner_pass": "Incorrect owner password.",
        "language_select": "Choose your language",
        "owner_pass": "Owner Password"
    }
}

selected_lang = "ITA"  # default

def start_app():
    root = tk.Tk()
    root.title("Clipo - Login / Registrazione")
    root.geometry("400x500")

    lang = LANGUAGES[selected_lang]

    # Fields
    tk.Label(root, text=lang["email"]).pack()
    email_entry = tk.Entry(root)
    email_entry.pack()

    tk.Label(root, text="Username").pack()
    username_entry = tk.Entry(root)
    username_entry.pack()

    tk.Label(root, text=lang["password"]).pack()
    password_entry = tk.Entry(root, show="*")
    password_entry.pack()

    tk.Label(root, text=lang["repeat_password"]).pack()
    repeat_password_entry = tk.Entry(root, show="*")
    repeat_password_entry.pack()

    tk.Label(root, text=lang["dob"]).pack()
    dob_entry = tk.Entry(root)
    dob_entry.pack()

    tk.Label(root, text=lang["human_test"]).pack()
    human_test_entry = tk.Entry(root)
    human_test_entry.pack()

    def submit():
        email = email_entry.get()
        username = username_entry.get()
        pwd1 = password_entry.get()
        pwd2 = repeat_password_entry.get()
        dob = dob_entry.get()
        human = human_test_entry.get()

        if human.strip() != "8":
            messagebox.showerror("Errore", lang["not_human"])
            return

        if username.lower() == "proprietario":
            # Richiedi password proprietario
            owner_pwd = tk.simpledialog.askstring("Admin", lang["owner_pass"], show="*")
            if owner_pwd != "GPconsultingClipo":
                messagebox.showerror("Errore", lang["wrong_owner_pass"])
                return
            open_admin_panel(email)
        else:
            # Normal registration/login
            auth = AuthManager()
            success, is_adult = auth.register_or_login(email, pwd1, pwd2, dob)
            if success:
                open_user_panel(email, is_adult)
            else:
                messagebox.showerror("Errore", "Errore durante accesso/registrazione.")

    tk.Button(root, text=lang["submit"], command=submit).pack(pady=10)

    root.mainloop()

def choose_language():
    lang_window = tk.Tk()
    lang_window.title("Clipo - Lingua")
    lang_window.geometry("300x200")

    tk.Label(lang_window, text="Seleziona la lingua / Choose your language").pack(pady=20)

    def set_language(lang_code):
        global selected_lang
        selected_lang = lang_code
        lang_window.destroy()
        start_app()

    ttk.Button(lang_window, text="Italiano", command=lambda: set_language("ITA")).pack(pady=5)
    ttk.Button(lang_window, text="English", command=lambda: set_language("ENG")).pack(pady=5)

    lang_window.mainloop()

if __name__ == "__main__":
    choose_language()
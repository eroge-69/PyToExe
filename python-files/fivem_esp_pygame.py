import tkinter as tk
from tkinter import font, ttk, messagebox
from PIL import Image, ImageTk
import subprocess
import os
import threading

# --- LoginApp ---
class LoginApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Administrator")
        self.configure(bg="#121212")
        self.geometry("330x400")
        self.resizable(False, False)

        self.font_title = font.Font(family="Segoe UI", size=16, weight="bold")
        self.font_input = font.Font(family="Segoe UI", size=10)
        self.font_button = font.Font(family="Segoe UI", size=10, weight="bold")

        self.create_widgets()

    def create_widgets(self):
        try:
            logo = Image.open("logo.png").resize((160, 160))
            self.logo_img = ImageTk.PhotoImage(logo)
            tk.Label(self, image=self.logo_img, bg="#121212").pack(pady=(25, 5))
        except:
            pass

        tk.Label(self, text="7.7.7 engine", font=self.font_title, fg="white", bg="#121212").pack(pady=(0, 20))

        self.username = tk.Entry(self, font=self.font_input, bg="#1f1f1f", fg="white",
                                 insertbackground="white", bd=0, relief="flat")
        self.username.insert(0, "Username")
        self.username.pack(padx=40, pady=(0, 12), ipady=8, fill="x")
        self.username.bind("<FocusIn>", lambda e: self.clear_placeholder(self.username, "Username"))

        pw_frame = tk.Frame(self, bg="#121212")
        pw_frame.pack(padx=40, pady=(0, 12), fill="x")

        self.password = tk.Entry(pw_frame, font=self.font_input, bg="#1f1f1f", fg="white",
                                 insertbackground="white", bd=0, relief="flat", show="*")
        self.password.insert(0, "Password")
        self.password.pack(side="left", expand=True, fill="x", ipady=8)
        self.password.bind("<FocusIn>", lambda e: self.clear_placeholder(self.password, "Password"))

        self.show_password = False
        self.toggle_btn = tk.Button(pw_frame, text="👁️", font=("Segoe UI", 10), bg="#1f1f1f", fg="white",
                                    bd=0, activebackground="#1f1f1f", command=self.toggle_password)
        self.toggle_btn.pack(side="right", padx=6)

        login_btn = tk.Button(self, text="Login", font=self.font_button, bg="red", fg="#121212",
                              activebackground="#00ff00", bd=0, relief="flat", command=self.login)
        login_btn.pack(pady=10, ipadx=10, ipady=8)

    def toggle_password(self):
        self.show_password = not self.show_password
        self.password.config(show="" if self.show_password else "*")

    def clear_placeholder(self, entry, default):
        if entry.get() == default:
            entry.delete(0, tk.END)

    def login(self):
        user = self.username.get()
        pwd = self.password.get()
        if user == "BUZZARDO" and pwd == "BUZZARDOACCES":
            self.destroy()
            LoadingScreen()
        else:
            messagebox.showerror("Errore", "Credenziali non valide")

# --- LoadingScreen ---
class LoadingScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Caricamento")
        self.configure(bg="#121212")
        self.geometry("300x200")
        self.resizable(False, False)

        self.label = tk.Label(self, text="Caricamento in corso...", fg="white", bg="#121212", font=("Segoe UI", 12))
        self.label.pack(pady=30)

        self.progress = ttk.Progressbar(self, mode="indeterminate", length=200)
        self.progress.pack(pady=10)
        self.progress.start(10)

        self.after(4000, self.open_main)

    def open_main(self):
        self.destroy()
        MainApp()

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Administrator")
        self.configure(bg="#121212")
        self.geometry("330x400")
        self.resizable(False, False)

        self.font_title = font.Font(family="Segoe UI", size=14, weight="bold")
        self.font_subtitle = font.Font(family="Segoe UI", size=9)
        self.font_button = font.Font(family="Segoe UI", size=10, weight="bold")

        self.create_widgets()

    def create_widgets(self):
        try:
            logo = Image.open("logo.png").resize((130, 130))
            self.logo_img = ImageTk.PhotoImage(logo)
            tk.Label(self, image=self.logo_img, bg="#121212").pack(pady=(25, 5))
        except:
            pass
        tk.Label(self, text="7.7.7 engine", font=self.font_title, fg="white", bg="#121212").pack(pady=(25, 2))
        tk.Label(self, text="STATUS: Undetected", font=self.font_subtitle, fg="gray", bg="#121212").pack()
        tk.Label(self, text="VERSION: 1.0", font=self.font_subtitle, fg="gray", bg="#121212").pack(pady=(0, 10))

        self.option_var = tk.StringVar(value="Cheat")
        options = ["Cheat"]  # Solo opzione exe come richiesto
        self.dropdown = ttk.Combobox(self, textvariable=self.option_var, values=options, state="readonly")
        self.dropdown.pack(pady=10, ipadx=4, ipady=2)

        execute_btn = tk.Button(self, text="Execute", font=self.font_button, bg="#2a2a2a", fg="white",
                                command=self.execute_option, bd=0, relief="flat")
        execute_btn.pack(pady=20, ipadx=10, ipady=8)

    def execute_option(self):
        option = self.option_var.get()
        if option == "Cheat":
            threading.Thread(target=self.run_exe_from, daemon=True).start()
        else:
            messagebox.showinfo("Info", "Seleziona l'opzione 'exe' per eseguire.")

    def run_exe_from(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        folder = os.path.join(base_dir, "internal", "opzione", "dll", "fresh", "itnernazional")

        if not os.path.isdir(folder):
            if self.winfo_exists():
                self.after(0, lambda: messagebox.showerror("Errore", f"Cartella '{folder}' non trovata."))
            return

        exe_files = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(".exe")]
        if not exe_files:
            if self.winfo_exists():
                self.after(0, lambda: messagebox.showinfo("Nessun file", f"Nessun file .exe trovato in '{folder}'."))
            return

        selected_exe = exe_files[0]
        try:
            subprocess.Popen(selected_exe)
            if self.winfo_exists():
                self.after(0, lambda: messagebox.showinfo("Avvio", f"Avviato: {os.path.basename(selected_exe)}"))
        except Exception as e:
            if self.winfo_exists():
                self.after(0, lambda: messagebox.showerror("Errore", f"Impossibile avviare il file.\n{str(e)}"))

# --- Avvio ---
if __name__ == "__main__":
    app = LoginApp()
    app.mainloop()

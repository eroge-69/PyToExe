import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from modules.db_init import init_db, log_action
from modules.login import LoginView
from modules.dashboard import Dashboard
from modules.pos import POS
from modules.employees import Employees
from modules.activity_log import ActivityLog

class App:
    def __init__(self, root):
        self.root = root
        self.user = None
        self.theme = "superhero"
        root.title("UPLINK CAR WASH SYSTEM")
        root.state('zoomed')  # fullscreen-like
        self.build_menu()
        init_db()
        self.show_login()

    def build_menu(self):
        menubar = ttk.Menu(self.root)
        appm = ttk.Menu(menubar, tearoff=0)
        appm.add_command(label="Fullscreen (F11)", command=self.toggle_fullscreen)
        appm.add_separator()
        appm.add_command(label="Ondoka", command=self.root.destroy)
        menubar.add_cascade(label="UPLINK", menu=appm)
        self.root.config(menu=menubar)
        self.root.bind("<F11>", lambda e: self.toggle_fullscreen())

    def toggle_fullscreen(self):
        if self.root.attributes("-fullscreen"):
            self.root.attributes("-fullscreen", False)
            self.root.state('zoomed')
        else:
            self.root.attributes("-fullscreen", True)

    def clear(self):
        for w in self.root.winfo_children():
            # keep menu intact
            if not isinstance(w, ttk.Menu):
                w.destroy()

    def show_login(self):
        self.clear()
        LoginView(self.root, self.on_login).pack(fill="both", expand=True)

    def on_login(self, user):
        self.user = user
        self.show_shell()

    def show_shell(self):
        self.clear()
        # Topbar
        top = ttk.Frame(self.root, padding=8, bootstyle="light")
        ttk.Label(top, text="UPLINK CAR WASH SYSTEM", font=("Segoe UI", 14, "bold")).pack(side="left")
        ttk.Label(top, text=f"{self.user['username']} ({self.user['role']})", bootstyle=SECONDARY).pack(side="right")
        ttk.Button(top, text="Ondoka", bootstyle=DANGER, command=self.logout).pack(side="right", padx=6)
        top.pack(fill="x")

        # Sidebar
        wrap = ttk.Frame(self.root); wrap.pack(fill="both", expand=True)
        side = ttk.Frame(wrap, width=220, bootstyle="dark"); side.pack(side="left", fill="y")
        self.main = ttk.Frame(wrap, padding=10); self.main.pack(side="right", fill="both", expand=True)

        # Nav buttons by role
        items = [("dash","Dashibodi"), ("pos","POS"), ("employees","Watumishi"), ("logs","Logs")]
        role_allow = {
            "washer": {"dash","pos"},
            "cashier": {"dash","pos"},
            "manager": {"dash","pos","employees","logs"},
            "admin": {"dash","pos","employees","logs"},
        }
        allowed = role_allow.get(self.user["role"], {"dash"})
        for key,label in items:
            if key not in allowed: continue
            ttk.Button(side, text=label, bootstyle=SECONDARY, width=22, command=lambda k=key:self.nav(k)).pack(fill="x", padx=10, pady=6)

        self.nav("dash")

    def nav(self, key):
        for w in self.main.winfo_children(): w.destroy()
        if key == "dash":
            Dashboard(self.main, self.user).pack(fill="both", expand=True)
        elif key == "pos":
            POS(self.main, self.user).pack(fill="both", expand=True)
        elif key == "employees":
            if self.user["role"] not in ("admin","manager"):
                messagebox.showerror("Ruhusa", "Huna ruhusa kuingia hapa."); return
            Employees(self.main, self.user).pack(fill="both", expand=True)
        elif key == "logs":
            if self.user["role"] not in ("admin","manager"):
                messagebox.showerror("Ruhusa", "Huna ruhusa kuingia hapa."); return
            ActivityLog(self.main).pack(fill="both", expand=True)

    def logout(self):
        log_action(self.user, "logout")
        self.user = None
        self.show_login()

def main():
    style = ttk.Style(theme="superhero")
    root = style.master
    App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
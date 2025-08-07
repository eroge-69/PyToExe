import tkinter as tk
from tkinter import messagebox, filedialog
import os
import base64
import mimetypes
import tempfile
import shutil
import json
from datetime import datetime

# ========== CONFIGURATION ==========
CONFIG_FILE = "enderfiles_config.json"
INTRUDER_THRESHOLD = 3
INITIAL_DEFAULT_PASSWORD = "password"

default_settings = {
    "owner_password": INITIAL_DEFAULT_PASSWORD,
    "theme": "dark",
    "bg_image": ""
}
settings = {}
login_attempts = 0
intruder_log = {"times": [], "added": 0, "deleted": 0}


def load_config():
    global settings
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                settings = json.load(f)
        except:
            settings = default_settings.copy()
    else:
        settings = default_settings.copy()
        save_config()


def save_config():
    with open(CONFIG_FILE, "w") as f:
        json.dump(settings, f, indent=4)


load_config()

# ========== MOCK VAULT DATA ==========
owner_vault = {
    "hello.txt": base64.b64encode(b"Hello, Owner! to ENDERFILES").decode("utf-8"),
    "notes.txt": base64.b64encode(b"Top secret notes.").decode("utf-8"),
}
intruder_vault = {
    "Owner.txt": base64.b64encode(b"Welcome to ENDERFILES").decode("utf-8"),
}

# ========== UTILITY FUNCTIONS ==========
def apply_theme(window, owner_mode=True):
    """
    Owner mode: dark/light + optional background image.
    Intruder mode: fixed grey.
    """
    if not owner_mode:
        bg, fg = "#808080", "#ffffff"
        window.configure(bg=bg)
        for w in window.winfo_children():
            try: w.configure(bg=bg, fg=fg)
            except: pass
        return

    # owner theme colors
    bg, fg = ("#2b2b2b", "#ffffff") if settings["theme"] == "dark" else ("#ffffff", "#000000")
    window.configure(bg=bg)

    # background image
    img_path = settings.get("bg_image", "")
    if img_path and os.path.exists(img_path):
        try:
            window.bg_img = tk.PhotoImage(file=img_path)
            lbl = tk.Label(window, image=window.bg_img)
            lbl.place(x=0, y=0, relwidth=1, relheight=1)
            lbl.lower()
        except:
            pass

    for w in window.winfo_children():
        try:
            # skip background label itself
            if isinstance(w, tk.Label) and getattr(w, "image", None):
                continue
            w.configure(bg=bg, fg=fg)
        except: pass


def decode_to_tempfile(encoded, fname):
    data = base64.b64decode(encoded)
    path = os.path.join(tempfile.gettempdir(), fname)
    with open(path, "wb") as f:
        f.write(data)
    return path


def cleanup_tempfile(path):
    try:
        os.remove(path)
    except:
        pass

# ========== SETTINGS WINDOW ==========
class SettingsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Settings")
        self.geometry("400x550")
        pad = 10

        # Theme toggle
        tk.Label(self, text="Theme:", font=("Arial", 12)).pack(
            anchor="w", padx=pad, pady=(pad, 5))
        tk.Button(self, text="Toggle Dark/Light Mode", command=self.toggle_theme
        ).pack(fill=tk.X, padx=pad)

        # Background image picker
        tk.Label(self, text="Background Image:", font=("Arial", 12)).pack(
            anchor="w", padx=pad, pady=(20, 5))
        tk.Button(self, text="Select Image…", command=self.select_bg_image
        ).pack(fill=tk.X, padx=pad)
        tk.Button(self, text="Remove Background Image", command=self.remove_bg_image
        ).pack(fill=tk.X, padx=pad, pady=(5, 0))

        # Current password display
        tk.Label(self, text="Current Password:", font=("Arial", 12)).pack(
            anchor="w", padx=pad, pady=(20, 5))
        self.current_pw_label = tk.Label(
            self, text="*" * len(settings["owner_password"]), font=("Arial", 10))
        self.current_pw_label.pack(anchor="w", padx=pad)

        # Show/hide checkbox
        self.show_pass_var = tk.BooleanVar(self)
        self.show_pass_var.set(False)
        tk.Checkbutton(self, text="Show password",
                       variable=self.show_pass_var,
                       command=self.toggle_show_password
        ).pack(anchor="w", padx=pad, pady=(5, 0))

        # New password entries
        tk.Label(self, text="New Password:", font=("Arial", 10)).pack(
            anchor="w", padx=pad, pady=(20, 0))
        self.new_pass = tk.Entry(self, show="*")
        self.new_pass.pack(fill=tk.X, padx=pad)

        tk.Label(self, text="Confirm New Password:", font=("Arial", 10)).pack(
            anchor="w", padx=pad, pady=(5, 0))
        self.confirm_pass = tk.Entry(self, show="*")
        self.confirm_pass.pack(fill=tk.X, padx=pad)

        # Save Settings button
        tk.Button(self, text="Save Settings", font=("Arial", 14, "bold"),
                  bg="#4CAF50", fg="white", activebackground="#45A049",
                  activeforeground="white", height=2, borderwidth=0,
                  command=self.save_settings
        ).pack(pady=20, padx=pad, fill=tk.X)

        apply_theme(self, owner_mode=True)
        apply_theme(self.master, owner_mode=True)

    def toggle_theme(self):
        settings["theme"] = "light" if settings["theme"] == "dark" else "dark"
        apply_theme(self, owner_mode=True)
        apply_theme(self.master, owner_mode=True)

    def select_bg_image(self):
        path = filedialog.askopenfilename(
            title="Select background image",
            filetypes=[("Image Files", "*.png;*.gif;*.jpg;*.jpeg"), ("All files", "*.*")]
        )
        if path:
            settings["bg_image"] = path
            apply_theme(self, owner_mode=True)
            apply_theme(self.master, owner_mode=True)

    def remove_bg_image(self):
        settings["bg_image"] = ""
        apply_theme(self, owner_mode=True)
        apply_theme(self.master, owner_mode=True)

    def toggle_show_password(self):
        if self.show_pass_var.get():
            self.current_pw_label.config(text=settings["owner_password"])
        else:
            self.current_pw_label.config(
                text="*" * len(settings["owner_password"]))

    def save_settings(self):
        new_pw = self.new_pass.get().strip()
        confirm_pw = self.confirm_pass.get().strip()
        if new_pw or confirm_pw:
            if new_pw != confirm_pw:
                messagebox.showerror("Error", "Passwords do not match.")
                return
            settings["owner_password"] = new_pw
        save_config()
        messagebox.showinfo("Settings Saved", "Your changes have been saved.")
        self.destroy()

# ========== LOGIN WINDOW ==========
class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Login to ENDERFILES")
        self.geometry("320x200")
        pad = 20

        tk.Label(self, text=f"Default Password: {INITIAL_DEFAULT_PASSWORD}",
                 font=("Arial", 10)).pack(pady=(pad, 5))
        tk.Label(self, text="Enter Password:", font=("Arial", 10)).pack()
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack(pady=5, padx=pad, fill=tk.X)
        self.password_entry.bind("<Return>", lambda e: self.login())
        tk.Button(self, text="Login", command=self.login).pack(pady=15)

        apply_theme(self, owner_mode=True)

    def login(self):
        global login_attempts, intruder_log
        pwd = self.password_entry.get()
        if pwd == settings["owner_password"]:
            if intruder_log["times"]:
                times = "\n".join(t.strftime("%Y-%m-%d %H:%M:%S") for t in intruder_log["times"])
                msg = (
                    "Intruder sign-in detected!\n\n"
                    f"Timestamps:\n{times}\n\n"
                    f"Files added: {intruder_log['added']}\n"
                    f"Files deleted: {intruder_log['deleted']}"
                )
                messagebox.showwarning("Intruder Alert", msg)
                intruder_log.clear()
                intruder_log.update({"times": [], "added": 0, "deleted": 0})
            self.destroy()
            VaultWindow(owner=True).mainloop()
            return

        login_attempts += 1
        remaining = INTRUDER_THRESHOLD - login_attempts
        if login_attempts < INTRUDER_THRESHOLD:
            messagebox.showerror("Login Failed", f"Incorrect password. {remaining} attempts left.")
        else:
            intruder_log["times"].append(datetime.now())
            messagebox.showwarning("Redirecting", "Redirecting to Owner Vault...")
            self.destroy()
            VaultWindow(owner=False).mainloop()

# ========== VAULT WINDOW ==========
class VaultWindow(tk.Tk):
    def __init__(self, owner=True):
        super().__init__()
        self.owner_mode = owner
        self.vault = owner_vault if owner else intruder_vault
        self.temp_files = []

        self.title("ENDERFILES Vault")
        self.geometry("600x400")
        pad = 10

        self.header = tk.Label(self, font=("Arial", 14))
        self.header.pack(pady=(pad, 0))
        self.update_header()

        self.listbox = tk.Listbox(self)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=pad, pady=(5, 0))
        self.populate_list()
        self.listbox.bind("<Double-1>", lambda e: self.view_file())

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=pad)
        actions = [("View", self.view_file), ("Delete", self.delete_file), ("Add", self.add_file)]
        if owner:
            actions += [("Transfer", self.transfer_file), ("Settings", self.open_settings),
                        ("Switch Vault", self.switch_vault)]
        actions.append(("Logout", self.logout))

        for txt, cmd in actions:
            tk.Button(btn_frame, text=txt, command=cmd).pack(side=tk.LEFT, padx=5)

        apply_theme(self, owner_mode=self.owner_mode)

    def update_header(self):
        if self.vault is owner_vault:
            self.header.config(text="Owner Vault — Access Granted")
        else:
            self.header.config(text="Owner Vault — Access Granted")

    def populate_list(self):
        self.listbox.delete(0, tk.END)
        for fname in self.vault:
            self.listbox.insert(tk.END, fname)

    def view_file(self):
        sel = self.listbox.curselection()
        if not sel:
            return messagebox.showwarning("Select File", "Choose a file first.")
        fname = self.listbox.get(sel[0])
        encoded = self.vault.get(fname)
        path = decode_to_tempfile(encoded, fname)
        self.temp_files.append(path)

        mime, _ = mimetypes.guess_type(path)
        popup = tk.Toplevel(self)
        popup.title(fname)
        txt = tk.Text(popup)
        if mime and mime.startswith("text"):
            content = "[Content hidden]" if not self.owner_mode else ""
            if self.owner_mode:
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                except:
                    content = "[Could not decode]"
            txt.insert(tk.END, content)
        else:
            txt.insert(tk.END, f"Opened file at {path}")
        txt.config(state=tk.DISABLED)
        txt.pack(expand=True, fill=tk.BOTH)
        apply_theme(popup, owner_mode=self.owner_mode)

    def add_file(self):
        src = filedialog.askopenfilename()
        if not src:
            return
        name = os.path.basename(src)
        with open(src, "rb") as f:
            enc = base64.b64encode(f.read()).decode("utf-8")
        if self.owner_mode:
            owner_vault[name] = enc
        else:
            intruder_vault[name] = enc
            intruder_log["added"] += 1
        self.vault[name] = enc
        self.listbox.insert(tk.END, name)

    def transfer_file(self):
        sel = self.listbox.curselection()
        if not sel:
            return messagebox.showwarning("Select File", "Choose a file first.")
        name = self.listbox.get(sel[0])
        path = decode_to_tempfile(self.vault[name], name)
        dest = filedialog.askdirectory()
        if not dest:
            return
        shutil.copy(path, os.path.join(dest, name))
        messagebox.showinfo("Transferred", f"{name} copied to {dest}")

    def delete_file(self):
        sel = self.listbox.curselection()
        if not sel:
            return messagebox.showwarning("Select File", "Choose a file first.")
        name = self.listbox.get(sel[0])
        if messagebox.askyesno("Confirm Delete", f"Delete {name}?"):
            del self.vault[name]
            if not self.owner_mode:
                intruder_log["deleted"] += 1
            self.listbox.delete(sel[0])

    def open_settings(self):
        SettingsWindow(self)

    def switch_vault(self):
        # toggle vault source
        self.vault = intruder_vault if self.vault is owner_vault else owner_vault
        self.update_header()
        self.populate_list()
        apply_theme(self, owner_mode=self.owner_mode)

    def logout(self):
        for p in self.temp_files:
            cleanup_tempfile(p)
        self.destroy()
        LoginWindow().mainloop()


# ========== RUN APPLICATION ==========
if __name__ == "__main__":
    LoginWindow().mainloop()

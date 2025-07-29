import customtkinter as ctk
from tkinter import simpledialog, messagebox, Menu
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
import base64
import os
from datetime import datetime

# App setup
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

APP_FOLDER = "notebook_pages"
CONFIG_FILE = "config.json"

if not os.path.exists(APP_FOLDER):
    os.makedirs(APP_FOLDER)

# Encryption functions
def get_key(password):
    hasher = SHA256.new(password.encode('utf-8'))
    return hasher.digest()

def encrypt(raw_data, password):
    key = get_key(password)
    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(raw_data.encode('utf-8'))
    return base64.b64encode(nonce + tag + ciphertext).decode('utf-8')

def decrypt(enc_data, password):
    enc = base64.b64decode(enc_data)
    key = get_key(password)
    nonce = enc[:16]
    tag = enc[16:32]
    ciphertext = enc[32:]
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    data = cipher.decrypt_and_verify(ciphertext, tag)
    return data.decode('utf-8')

# Password logic
def get_password():
    if not os.path.exists(CONFIG_FILE):
        pw1 = simpledialog.askstring("Set Password", "Set a new password:", show='*')
        if pw1 is None or pw1.strip() == "":
            messagebox.showinfo("Cancelled", "Password setup cancelled.")
            exit()
        pw2 = simpledialog.askstring("Confirm Password", "Confirm password:", show='*')
        if pw2 is None or pw1 != pw2:
            messagebox.showerror("Error", "Password mismatch or cancelled.")
            exit()
        with open(CONFIG_FILE, "w") as f:
            f.write(encrypt(pw1, pw1))
        return pw1
    else:
        for _ in range(3):
            pw = simpledialog.askstring("Enter Password", "Enter your notebook password:", show='*')
            if pw is None:
                messagebox.showinfo("Cancelled", "Login cancelled.")
                exit()
            try:
                with open(CONFIG_FILE, "r") as f:
                    encrypted_pw = f.read()
                if decrypt(encrypted_pw, pw) == pw:
                    return pw
                else:
                    messagebox.showwarning("Wrong", "Incorrect password.")
            except:
                messagebox.showerror("Error", "Failed to verify password.")
        messagebox.showerror("Access Denied", "Too many failed attempts.")
        exit()

# Main App
class SecureNotebook(ctk.CTk):
    def __init__(self, master_password):
        super().__init__()
        self.title("📒 Secure Notebook")
        self.geometry("900x600")
        self.master_password = master_password
        self.pages = {}
        self.current_page = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)

        self.add_button = ctk.CTkButton(self.sidebar, text="+ New Entry", command=self.add_entry)
        self.add_button.pack(pady=10, padx=10)

        self.page_list_frame = ctk.CTkScrollableFrame(self.sidebar, width=180, height=500)
        self.page_list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Editor
        self.editor = ctk.CTkTextbox(self, font=("Consolas", 14))
        self.editor.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.load_all_pages()
        self.auto_save()

    def auto_save(self):
        self.save_current_page()
        self.after(5000, self.auto_save)

    def add_entry(self):
        today = datetime.now().strftime("%Y-%m-%d")
        time_now = datetime.now().strftime("%H:%M")
        filename = f"{today}.enc"
        path = os.path.join(APP_FOLDER, filename)

        if os.path.exists(path):
            with open(path, "r") as f:
                enc_data = f.read()
            try:
                content = decrypt(enc_data, self.master_password)
            except:
                messagebox.showerror("Error", "Failed to decrypt page.")
                return
            content += f"\n\n----- New Entry at {time_now} -----\n"
        else:
            content = f"----- New Entry at {time_now} -----\n"
            self.create_page_button(today)

        with open(path, "w") as f:
            f.write(encrypt(content, self.master_password))

        self.load_page(today)

    def create_page_button(self, title):
        btn = ctk.CTkButton(self.page_list_frame, text=title, width=160, anchor="w", fg_color="transparent")
        btn.pack(pady=5)

        def open_page(e=None): self.load_page(title)
        def show_context_menu(event):
            menu = Menu(self, tearoff=0)
            menu.add_command(label="Rename", command=lambda: self.rename_page(title))
            menu.add_command(label="Delete", command=lambda: self.delete_page(title))
            menu.tk_popup(event.x_root, event.y_root)

        btn.bind("<Button-1>", open_page)
        btn.bind("<Button-3>", show_context_menu)

        self.pages[title] = btn

    def load_all_pages(self):
        for fname in sorted(os.listdir(APP_FOLDER)):
            if fname.endswith(".enc"):
                title = fname.replace(".enc", "")
                self.create_page_button(title)

    def load_page(self, title):
        self.save_current_page()
        path = os.path.join(APP_FOLDER, f"{title}.enc")
        try:
            with open(path, "r") as f:
                enc_data = f.read()
            text = decrypt(enc_data, self.master_password)
            self.editor.delete("1.0", "end")
            self.editor.insert("1.0", text)
            self.current_page = title
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load page:\n{e}")

    def save_current_page(self):
        if not self.current_page:
            return
        text = self.editor.get("1.0", "end").strip()
        path = os.path.join(APP_FOLDER, f"{self.current_page}.enc")
        with open(path, "w") as f:
            f.write(encrypt(text, self.master_password))

    def rename_page(self, old_title):
        new_title = simpledialog.askstring("Rename", f"Rename '{old_title}' to:")
        if not new_title:
            return
        old_path = os.path.join(APP_FOLDER, f"{old_title}.enc")
        new_path = os.path.join(APP_FOLDER, f"{new_title}.enc")
        if os.path.exists(new_path):
            messagebox.showerror("Error", "A page with that name already exists.")
            return
        os.rename(old_path, new_path)
        self.pages[old_title].destroy()
        del self.pages[old_title]
        self.create_page_button(new_title)
        if self.current_page == old_title:
            self.current_page = new_title

    def delete_page(self, title):
        confirm = messagebox.askyesno("Delete Page", f"Are you sure you want to delete '{title}'?")
        if not confirm:
            return
        path = os.path.join(APP_FOLDER, f"{title}.enc")
        if os.path.exists(path):
            os.remove(path)
        self.pages[title].destroy()
        del self.pages[title]
        if self.current_page == title:
            self.editor.delete("1.0", "end")
            self.current_page = None

    def on_close(self):
        self.save_current_page()
        self.destroy()

# Run app
if __name__ == "__main__":
    password = get_password()
    app = SecureNotebook(password)
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()

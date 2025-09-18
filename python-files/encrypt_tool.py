"""
Secret Message Encryptor — Final Colorful Version
-------------------------------------------------
Features:
- Strong encryption using Fernet (cryptography lib)
- Password-based key (derived from password + salt)
- Encrypt with password
- Decrypt always asks for password via popup
- Save/Load encrypted file
- Copy to clipboard
- Tkinter GUI (resizable, maximized window)
- Colorful UI
- Toggle password visibility
"""

import os
import base64
import secrets
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet, InvalidToken


# ---------- Utilities: Key derivation ----------

def derive_key_from_password(password: str, salt: bytes, iterations: int = 390000) -> bytes:
    """Derive a Fernet key from password and salt."""
    password_bytes = password.encode('utf-8')
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
        backend=default_backend()
    )
    key = kdf.derive(password_bytes)
    return base64.urlsafe_b64encode(key)


def generate_salt(length: int = 16) -> bytes:
    return secrets.token_bytes(length)


def generate_strong_password(length: int = 16) -> str:
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_+="
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def pack_encrypted_data(salt: bytes, token: bytes) -> bytes:
    """Pack salt + token: 1 byte salt length | salt | token"""
    slen = len(salt)
    return bytes([slen]) + salt + token


def unpack_encrypted_data(data: bytes):
    """Unpack salt + token"""
    slen = data[0]
    salt = data[1:1+slen]
    token = data[1+slen:]
    return salt, token


# ---------- GUI ----------

class EncryptorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Secret Message Encryptor")
        self.geometry("950x700")
        self.minsize(750, 600)
        self.configure(bg="#1e1e2f")  # Dark vibrant background
        self.setup_styles()
        self.create_widgets()

    def setup_styles(self):
        style = ttk.Style(self)
        try:
            style.theme_use('clam')
        except:
            pass

        # Colors
        bg_color = "#1e1e2f"
        fg_color = "#f0f0f0"
        accent_color = "#00ffff"
        button_bg = "#ff6f61"
        button_hover = "#ffa07a"
        entry_bg = "#5e4b8b"
        entry_fg = "#f0f0f0"

        # General styles
        self.configure(bg=bg_color)
        style.configure('.', background=bg_color, foreground=fg_color, font=('Segoe UI', 11))
        style.configure('TLabel', background=bg_color, foreground=fg_color, font=('Segoe UI', 12))
        style.configure('Header.TLabel', font=('Segoe UI', 20, 'bold'), foreground=accent_color, background=bg_color)
        style.configure('TButton',
                        background=button_bg,
                        foreground=fg_color,
                        font=('Segoe UI', 11, 'bold'),
                        padding=8)
        style.map('TButton',
                  background=[('active', button_hover), ('pressed', accent_color)],
                  foreground=[('active', '#f0f0f0'), ('pressed', '#1e1e2f')])

        style.configure('TEntry',
                        fieldbackground=entry_bg,
                        foreground=entry_fg,
                        padding=6,
                        font=('Segoe UI', 11))
        style.configure('TFrame', background=bg_color)

    def create_widgets(self):
        header = ttk.Label(self, text="Secret Message Encryptor", style='Header.TLabel')
        header.pack(pady=(20, 15))

        main_frame = ttk.Frame(self, padding=20, style='TFrame')
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)

        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=0)
        main_frame.columnconfigure(2, weight=0)
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)

        ttk.Label(main_frame, text="Enter Message (Plaintext):").grid(row=0, column=0, sticky='w', pady=(0,6))

        self.txt_input = tk.Text(main_frame, height=8, wrap='word', font=('Consolas', 11),
                                 bg="#5e4b8b", fg="#f0f0f0", insertbackground="#f0f0f0",
                                 relief='flat', bd=0)
        self.txt_input.grid(row=1, column=0, columnspan=3, sticky='nsew', pady=(0, 15))

        ttk.Label(main_frame, text="Password (for encryption):").grid(row=2, column=0, sticky='w', pady=(0,6))

        self.pw_var = tk.StringVar()
        self.pw_entry = ttk.Entry(main_frame, textvariable=self.pw_var, show='*', width=30)
        self.pw_entry.grid(row=2, column=1, sticky='w', pady=(0,6))

        # Toggle password visibility
        def toggle_password():
            if self.pw_entry.cget('show') == '':
                self.pw_entry.config(show='*')
                toggle_btn.config(text='Show')
            else:
                self.pw_entry.config(show='')
                toggle_btn.config(text='Hide')

        toggle_btn = ttk.Button(main_frame, text='Show', width=6, command=toggle_password)
        toggle_btn.grid(row=2, column=2, sticky='w', padx=(10,0), pady=(0,6))

        gen_pw_btn = ttk.Button(main_frame, text="Generate Password", command=self.generate_password)
        gen_pw_btn.grid(row=2, column=3, sticky='w', padx=(10,0), pady=(0,6))

        btn_frame = ttk.Frame(main_frame, style='TFrame')
        btn_frame.grid(row=3, column=0, columnspan=4, sticky='w', pady=(10, 20))

        btn_width = 16
        ttk.Button(btn_frame, text="Encrypt →", command=self.encrypt_message, width=btn_width).grid(row=0, column=0, padx=6)
        ttk.Button(btn_frame, text="Decrypt ←", command=self.decrypt_message, width=btn_width).grid(row=0, column=1, padx=6)
        ttk.Button(btn_frame, text="Save Encrypted", command=self.save_encrypted_to_file, width=btn_width).grid(row=0, column=2, padx=6)
        ttk.Button(btn_frame, text="Load Encrypted", command=self.load_encrypted_from_file, width=btn_width).grid(row=0, column=3, padx=6)
        ttk.Button(btn_frame, text="Copy Output", command=self.copy_output, width=btn_width).grid(row=0, column=4, padx=6)

        ttk.Label(main_frame, text="Output (Encrypted / Decrypted):").grid(row=4, column=0, sticky='w', pady=(0,6))

        self.txt_output = tk.Text(main_frame, height=10, wrap='word', font=('Consolas', 11),
                                  bg="#5e4b8b", fg="#f0f0f0", insertbackground="#f0f0f0",
                                  relief='flat', bd=0)
        self.txt_output.grid(row=5, column=0, columnspan=4, sticky='nsew')

        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self, textvariable=self.status_var, anchor='w',
                               background="#3b4252", foreground="#00ffff", font=('Segoe UI', 10))
        status_bar.pack(fill='x', side='bottom', ipady=4)

    # ---------- Button actions ----------

    def generate_password(self):
        pw = generate_strong_password(16)
        self.pw_var.set(pw)
        self.clipboard_clear()
        self.clipboard_append(pw)
        self.status_var.set("Generated strong password and copied to clipboard.")

    def encrypt_message(self):
        plaintext = self.txt_input.get("1.0", "end").strip()
        password = self.pw_var.get().strip()
        if not plaintext:
            messagebox.showwarning("Input Required", "Enter a message to encrypt.")
            return
        if not password:
            messagebox.showwarning("Password Required", "Enter or generate a password.")
            return
        try:
            salt = generate_salt()
            key = derive_key_from_password(password, salt)
            f = Fernet(key)
            token = f.encrypt(plaintext.encode('utf-8'))
            packed = pack_encrypted_data(salt, token)
            b64 = base64.urlsafe_b64encode(packed).decode('utf-8')
            self.txt_output.delete("1.0", "end")
            self.txt_output.insert("1.0", b64)
            self.status_var.set("Encryption successful.")
        except Exception as e:
            messagebox.showerror("Error", f"Encryption failed:\n{e}")
            self.status_var.set("Encryption failed.")

    def decrypt_message(self):
        data_b64 = self.txt_output.get("1.0", "end").strip() or self.txt_input.get("1.0", "end").strip()
        if not data_b64:
            messagebox.showwarning("Input Required", "Paste/load the encrypted data first.")
            return
        password = simpledialog.askstring("Password Required", "Enter password to decrypt:", show='*', parent=self)
        if not password:
            return
        try:
            packed = base64.urlsafe_b64decode(data_b64.encode('utf-8'))
            salt, token = unpack_encrypted_data(packed)
            key = derive_key_from_password(password, salt)
            f = Fernet(key)
            plaintext = f.decrypt(token).decode('utf-8')
            self.txt_output.delete("1.0", "end")
            self.txt_output.insert("1.0", plaintext)
            self.status_var.set("Decryption successful.")
        except InvalidToken:
            messagebox.showerror("Decryption Failed", "Wrong password or corrupted data.")
            self.status_var.set("Decryption failed.")
        except Exception as e:
            messagebox.showerror("Error", f"Error during decryption:\n{e}")
            self.status_var.set("Decryption failed.")

    def save_encrypted_to_file(self):
        data_b64 = self.txt_output.get("1.0", "end").strip()
        if not data_b64:
            messagebox.showwarning("Nothing to Save", "No encrypted data to save.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".enc", filetypes=[("Encrypted files","*.enc")])
        if not file_path:
            return
        try:
            packed = base64.urlsafe_b64decode(data_b64.encode('utf-8'))
            with open(file_path, "wb") as f:
                f.write(packed)
            self.status_var.set(f"Saved encrypted file: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Save failed:\n{e}")

    def load_encrypted_from_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Encrypted files","*.enc"), ("All files","*.*")])
        if not file_path:
            return
        try:
            with open(file_path, "rb") as f:
                packed = f.read()
            data_b64 = base64.urlsafe_b64encode(packed).decode('utf-8')
            self.txt_output.delete("1.0", "end")
            self.txt_output.insert("1.0", data_b64)
            self.status_var.set(f"Loaded encrypted file: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Load failed:\n{e}")

    def copy_output(self):
        out = self.txt_output.get("1.0", "end").strip()
        if not out:
            messagebox.showwarning("Nothing to Copy", "Output is empty.")
            return
        self.clipboard_clear()
        self.clipboard_append(out)
        self.status_var.set("Output copied to clipboard.")


# ---------- Run ----------
if __name__ == "__main__":
    app = EncryptorApp()
    app.mainloop()

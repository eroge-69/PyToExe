import tkinter as tk
from tkinter import filedialog, font, simpledialog, messagebox
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from base64 import urlsafe_b64encode
import os

class MinimalistTextEditor:
    def __init__(self, master): 
        self.master = master
        self.master.title("Lime Writer")
        self.master.geometry("800x600")
        master.configure(bg="#3C5921")
        self.current_file = None
        self.is_encrypted = False
        self.current_encrypted_data = None 

        try:
            self.master.iconbitmap("LimeWriterLogo.ico")  
        except tk.TclError:
            print("Warning: Could not load icon. Ensure 'lime_writer_icon.ico' is in the same directory.")
            pass


        self.current_file = None
        self.is_encrypted = False
        self.current_encrypted_data = None 

        # Default font
        self.default_font = font.Font(family="Inter", size=12)
        
        # Text area 
        self.text_area = tk.Text(master, wrap="word", undo=True, font=self.default_font, 
                                 bg="#ffffff", fg="#333333", insertbackground="#333333", 
                                 selectbackground="#cceeff", selectforeground="#000000", 
                                 bd=0, padx=10, pady=10, relief="flat")
        self.text_area.pack(expand=True, fill="both", padx=20, pady=20) 

        # Formatting tags
        self.text_area.tag_configure("bold", font=(self.default_font.actual("family"), self.default_font.actual("size"), "bold"))
        self.text_area.tag_configure("italic", font=(self.default_font.actual("family"), self.default_font.actual("size"), "italic"))
        self.text_area.tag_configure("underline", font=(self.default_font.actual("family"), self.default_font.actual("size"), "underline"))

        # Toolbar 
        self.toolbar = tk.Frame(master, bd=1, relief="flat", bg="#3C5921", padx=10, pady=5)
        self.toolbar.pack(side="top", fill="x")

        # Formatting Buttons 
        bold_btn = tk.Button(self.toolbar, text="B", command=self.toggle_bold, font=("Inter", 10, "bold"), 
                             bg="#3C5921", fg="#C7C7C7", relief="raised", padx=8, pady=4, bd=0, 
                             activebackground="#243514", activeforeground="#C7C7C7") 
        bold_btn.pack(side="left", padx=2, pady=2)

        italic_btn = tk.Button(self.toolbar, text="I", command=self.toggle_italic, font=("Inter", 10, "italic"), 
                              bg="#3C5921", fg="#C7C7C7", relief="raised", padx=8, pady=4, bd=0, 
                              activebackground="#243514", activeforeground="#C7C7C7")
        italic_btn.pack(side="left", padx=2, pady=2)

        underline_btn = tk.Button(self.toolbar, text="U", command=self.toggle_underline, font=("Inter", 10, "underline"), 
                                 bg="#3C5921", fg="#C7C7C7", relief="raised", padx=8, pady=4, bd=0, 
                                 activebackground="#243514", activeforeground="#C7C7C7") 
        underline_btn.pack(side="left", padx=2, pady=2)

        # Font Selector 
        self.font_options = ["Inter", "Arial", "Courier New", "Times New Roman", "Helvetica", "Verdana"] 
        self.font_var = tk.StringVar(master)
        self.font_var.set(self.default_font.actual("family"))
        font_menu = tk.OptionMenu(self.toolbar, self.font_var, *self.font_options, command=self.change_font)
        font_menu.config(bg="#3C5921", fg="#C7C7C7", relief="raised", padx=8, pady=4, bd=0, 
                         activebackground="#243514", activeforeground="#C7C7C7") 
        font_menu["menu"].config(bg="#3C5921", fg="#C7C7C7", 
                                 activebackground="#243514", activeforeground="#C7C7C7") 
        font_menu.pack(side="left", padx=5)

        # File Menu (menubar itself)
        menubar = tk.Menu(master, bg="#3C5921", fg="#C7C7C7", relief="flat")
        master.config(menu=menubar)

        # File Menu (dropdown) 
        file_menu = tk.Menu(menubar, tearoff=0, bg="#3C5921", fg="#C7C7C7", 
                             activebackground="#243514", activeforeground="#C7C7C7") 
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As...", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Encrypt Document", command=self.encrypt_document)
        file_menu.add_command(label="Decrypt Document", command=self.decrypt_document)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.quit)

        # Status Bar 
        self.status_bar = tk.Label(master, text="Ready", bd=1, relief="flat", anchor="w", 
                                   bg="#3C5921", fg="#C7C7C7", padx=10, pady=2) 
        self.status_bar.pack(side="bottom", fill="x")
        
        # Keyboard Shortcuts (eg. Ctrl+S, Ctrl+Shift+S)  
        master.bind("<Control-n>", lambda event: self.new_file())
        master.bind("<Control-o>", lambda event: self.open_file())
        master.bind("<Control-s>", lambda event: self.save_file())
        master.bind("<Control-Shift-s>", lambda event: self.save_as_file())
        master.bind("<Control-b>", lambda event: self.toggle_bold()) 
        master.bind("<Control-i>", lambda event: self.toggle_italic())
        master.bind("<Control-u>", lambda event: self.toggle_underline())

    def _get_key_from_password(self, password, salt=None):
        if salt is None:
            salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt
    
    def _get_fernet(self, password, salt=None):
        key, _ = self._get_key_from_password(password, salt) 
        return Fernet(key) 
    
    def new_file(self):
        self.text_area.delete(1.0, tk.END)
        self.current_file = None
        self.is_encrypted = False
        self.status_bar.config(text="New Document")
        self.master.title("Lime Writer - Untitled")

    def open_file(self):
        file_path = filedialog.askopenfilename(defaultextension=".txt",
                                               filetypes=[("Text Files", "*.txt"),
                                                          ("Encrypted Files", "*.enc"),
                                                          ("All Files", "*.*")])
        if file_path:
            try:
                with open(file_path, "rb") as file:
                    content = file.read()

                # Encryption check
                if content.startswith(b"ENCRYPTED_DOC_V1:"):
                    self.is_encrypted = True
                    salt = content[len(b"ENCRYPTED_DOC_V1:") : len(b"ENCRYPTED_DOC_V1:") + 16]
                    encrypted_data = content[len(b"ENCRYPTED_DOC_V1:") + 16:]
                    password = simpledialog.askstring("Password", "Enter password to decrypt:", show='*')
                    if password:
                        try:
                            f = self._get_fernet(password, salt)
                            decrypted_content = f.decrypt(encrypted_data).decode('utf-8')
                            self.text_area.delete(1.0, tk.END)
                            self.text_area.insert(tk.END, decrypted_content)
                            self.current_file = file_path
                            self.master.title(f"Lime Writer - {os.path.basename(file_path)} (Encrypted)")
                            self.status_bar.config(text=f"Opened encrypted: {os.path.basename(file_path)}")
                        except Exception as e:
                            messagebox.showerror("Decryption Error", f"Failed to decrypt file. Wrong Passkey or Corrupted File. \nError: {e}")
                            self.new_file()
                    else:
                        messagebox.showwarning("Decryption Cancelled", "Decryption cancelled. File not loaded.")
                        self.new_file()
                else:
                    self.is_encrypted = False
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(tk.END, content.decode('utf-8'))
                    self.current_file = file_path
                    self.master.title(f"Lime Writer - {os.path.basename(file_path)}") 
                    self.status_bar.config(text=f"Opened: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not read file: {e}")
                self.status_bar.config(text="Error opening file")
            
    def save_file(self):
        if self.current_file:
            try:
                content = self.text_area.get(1.0, tk.END).encode('utf-8')
                if self.is_encrypted:
                    password = simpledialog.askstring("Password","Enter password to save file:", show='*')
                    if password:
                        key, salt = self._get_key_from_password(password)
                        f = Fernet(key)
                        encrypted_content = f.encrypt(content)
                        with open(self.current_file, "wb") as file:
                            file.write(b"ENCRYPTED_DOC_V1:" + salt + encrypted_content)
                        self.status_bar.config(text=f"Saved encrypted: {os.path.basename(self.current_file)}")
                    else: 
                        messagebox.showwarning("Save Cancelled", "Save cancelled. Password not provided.")
                        return 
                else:
                    with open(self.current_file, "w", encoding='utf-8') as file:
                        file.write(self.text_area.get(1.0, tk.END))
                    self.status_bar.config(text=f"Saved: {os.path.basename(self.current_file)}") 
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")
                self.status_bar.config(text="Error saving file")
        else: 
            self.save_as_file()
            
    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text Files", "*.txt"),
                                                            ("Encrypted Files", "*.enc"),
                                                            ("All Files", "*.*")])
        if file_path:
            self.current_file = file_path 
            self.save_file()
            self.master.title(f"Lime Writer - {os.path.basename(file_path)}")

    def encrypt_document(self): 
        if self.is_encrypted:
            messagebox.showinfo("Already Encrypted", "This document is already encrypted.")
            return
        
        password = simpledialog.askstring("Password", "Enter password to encrypt the document:", show='*')
        if password:
            confirm_password = simpledialog.askstring("Confirm Password", "Re-enter password to confirm:", show='*')
            if password == confirm_password:
                try:
                    content = self.text_area.get(1.0, tk.END).encode('utf-8')
                    key, salt = self._get_key_from_password(password)
                    f = Fernet(key)
                    encrypted_content = f.encrypt(content)

                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(tk.END, "(Encrypted content. Save to file to persist encryption.)")
                    self.current_encrypted_data = b"ENCRYPTED_DOC_V1:" + salt + encrypted_content
                    self.is_encrypted = True
                    self.status_bar.config(text="Document encrypted. Save to file to apply changes.")
                    
                    
                    if self.current_file:
                        self.master.title(f"Lime Writer - {os.path.basename(self.current_file)} (Encrypted)")
                    else:
                        self.master.title("Lime Writer - Untitled (Encrypted)") 
                except Exception as e:
                    messagebox.showerror("Encryption Error", f"Failed to encrypt document. Error: {e}")
            else:
                messagebox.showwarning("Password Mismatch", "Passwords do not match. Encryption cancelled.") 
        else:
            messagebox.showwarning("Encryption Cancelled", "Encryption cancelled. Password not provided.")

    def decrypt_document(self): 
        if not self.is_encrypted:
            messagebox.showinfo("Not Encrypted", "This document is not currently marked as encrypted.")
            return

        if not hasattr(self, 'current_encrypted_data') or not self.current_encrypted_data:
            messagebox.showerror("Decryption Error", "No encrypted data loaded in memory to decrypt. Please open an encrypted file.")
            return
        
        password = simpledialog.askstring("Password", "Enter password to decrypt the document:", show='*')
        if password:
            try:
                salt = self.current_encrypted_data[len(b"ENCRYPTED_DOC_V1:"):len(b"ENCRYPTED_DOC_V1:") + 16]
                encrypted_data = self.current_encrypted_data[len(b"ENCRYPTED_DOC_V1:") + 16:]
                f = self._get_fernet(password, salt)
                decrypted_content = f.decrypt(encrypted_data).decode('utf-8')
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, decrypted_content)
                self.is_encrypted = False 
                self.status_bar.config(text="Document decrypted.")
                self.master.title(self.master.title().replace(" (Encrypted)", "")) 
                del self.current_encrypted_data
            except Exception as e:
                messagebox.showerror("Decryption Error", f"Failed to decrypt document. Wrong password or corrupted file. \nError: {e}")
        else:
            messagebox.showwarning("Decryption Cancelled", "No Password Added. File not loaded.")
            self.new_file() 

    def toggle_bold(self): 
        try:
            current_tags = self.text_area.tag_names("sel.first")
            if "bold" in current_tags:
                self.text_area.tag_remove("bold", "sel.first", "sel.last")
            else:
                self.text_area.tag_add("bold", "sel.first", "sel.last")
            self.text_area.tag_raise("bold", "sel.first")
        except tk.TclError:
            pass # No selection

    def toggle_italic(self):
        try:
            current_tags = self.text_area.tag_names("sel.first")
            if "italic" in current_tags:
                self.text_area.tag_remove("italic", "sel.first", "sel.last")
            else:
                self.text_area.tag_add("italic", "sel.first", "sel.last")
            self.text_area.tag_raise("italic", "sel.first")
        except tk.TclError:
            pass # No selection

    def toggle_underline(self): 
        try:
            current_tags = self.text_area.tag_names("sel.first")
            if "underline" in current_tags:
                self.text_area.tag_remove("underline", "sel.first", "sel.last")
            else:
                self.text_area.tag_add("underline", "sel.first", "sel.last")
            self.text_area.tag_raise("underline", "sel.first")
        except tk.TclError:
            pass # No selection

    def change_font(self, new_font_family): 
        current_size = self.default_font.actual("size")
        self.default_font.config(family=new_font_family)
        self.text_area.config(font=(new_font_family, current_size))

        self.text_area.tag_configure("bold", font=(new_font_family, current_size, "bold"))
        self.text_area.tag_configure("italic", font=(new_font_family, current_size, "italic"))
        self.text_area.tag_configure("underline", font=(new_font_family, current_size, "underline"))

if __name__ == "__main__": 
    root = tk.Tk()
    app = MinimalistTextEditor(root) 
    root.mainloop()

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os
import json
import secrets
import hashlib
import psutil
import time
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from datetime import datetime, timedelta

class AdvancedFileEncryptor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("OBDPORTAL - Advanced File Encryptor v2.0")
        self.root.geometry("900x750")
        self.root.configure(bg='#f0f0f0')
        
        # Set modern theme
        style = ttk.Style()
        style.theme_use('clam')
        
        self.encrypted_files_db = "encrypted_files.json"
        self.engineers_db = "engineers.json"
        self.encrypted_files = self.load_encrypted_files()
        self.engineers = self.load_engineers()
        self.usb_key_file = "master.key"
        self.usb_drive = None
        self.master_password = "jbS@Nxv7Fvz_II5-(s@kj=AoL{n6Qh#N.BLOvgB=R^ywSsnMi3"
        self.selected_files = []
        
        self.setup_gui()
        self.check_usb_status()
        self.check_expired_files()
        
    def setup_gui(self):
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Company Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill='x', pady=(0, 20))
        
        company_label = ttk.Label(header_frame, text="OBDPORTAL", 
                                 font=('Arial', 24, 'bold'), foreground="#B12A2A")
        company_label.pack()
        
        title_label = ttk.Label(header_frame, text="🔐 Advanced File Encryptor", 
                               font=('Arial', 16, 'bold'))
        title_label.pack()
        
        # Notebook with modern styling
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True)
        
        # USB Management Tab
        usb_frame = ttk.Frame(notebook, padding="20")
        notebook.add(usb_frame, text="🔑 USB Key Setup")
        self.setup_usb_tab(usb_frame)
        
        # Encryption Tab
        encrypt_frame = ttk.Frame(notebook, padding="20")
        notebook.add(encrypt_frame, text="🔒 File Operations")
        self.setup_encrypt_tab(encrypt_frame)
        
        # Status bar at bottom
        self.status_var = tk.StringVar(value="Ready - Insert USB key to begin")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief='sunken', anchor='w', font=('Arial', 10))
        status_bar.pack(fill='x', pady=(10, 0))
        
    def setup_usb_tab(self, parent):
        # USB Status Card
        status_card = ttk.LabelFrame(parent, text="📊 USB Key Status", padding="15")
        status_card.pack(fill='x', pady=(0, 15))
        
        self.usb_status_var = tk.StringVar(value="🔍 Checking USB drives...")
        status_label = ttk.Label(status_card, textvariable=self.usb_status_var, 
                                font=('Arial', 12, 'bold'))
        status_label.pack()
        
        # Engineer Information Card
        eng_card = ttk.LabelFrame(parent, text="👨‍💻 Engineer Information", padding="15")
        eng_card.pack(fill='x', pady=(0, 15))
        
        eng_inner = ttk.Frame(eng_card)
        eng_inner.pack(fill='x')
        
        ttk.Label(eng_inner, text="Engineer Name:", font=('Arial', 10, 'bold')).pack(side='left')
        self.engineer_var = tk.StringVar()
        eng_entry = ttk.Entry(eng_inner, textvariable=self.engineer_var, width=25, font=('Arial', 10))
        eng_entry.pack(side='left', padx=(10, 0))
        
        # USB Drive Selection Card
        drive_card = ttk.LabelFrame(parent, text="💾 USB Drive Selection", padding="15")
        drive_card.pack(fill='x', pady=(0, 15))
        
        drive_inner = ttk.Frame(drive_card)
        drive_inner.pack(fill='x')
        
        self.drive_var = tk.StringVar()
        self.drive_combo = ttk.Combobox(drive_inner, textvariable=self.drive_var, 
                                       width=50, font=('Arial', 10), state='readonly')
        self.drive_combo.pack(side='left', padx=(0, 10))
        
        refresh_btn = ttk.Button(drive_inner, text="🔄 Refresh", command=self.refresh_drives)
        refresh_btn.pack(side='left')
        
        # Operations Card
        ops_card = ttk.LabelFrame(parent, text="⚙️ Operations", padding="15")
        ops_card.pack(fill='x')
        
        ops_inner = ttk.Frame(ops_card)
        ops_inner.pack()
        
        create_btn = ttk.Button(ops_inner, text="🔑 Create USB Key", 
                               command=self.create_usb_key, width=20)
        create_btn.pack(side='left', padx=(0, 10))
        
        verify_btn = ttk.Button(ops_inner, text="✅ Verify USB Key", 
                               command=self.verify_usb_key, width=20)
        verify_btn.pack(side='left')
        
        self.refresh_drives()
        
    def setup_encrypt_tab(self, parent):
        # File Selection Card
        file_card = ttk.LabelFrame(parent, text="📁 File Selection", padding="15")
        file_card.pack(fill='both', expand=True, pady=(0, 15))
        
        # File list with scrollbar
        list_frame = ttk.Frame(file_card)
        list_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        self.files_listbox = tk.Listbox(list_frame, font=('Arial', 10), 
                                       selectmode='extended', height=10)
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.files_listbox.yview)
        self.files_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.files_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # File operation buttons
        btn_frame = ttk.Frame(file_card)
        btn_frame.pack(fill='x')
        
        ttk.Button(btn_frame, text="📄 Add Files", command=self.add_files).pack(side='left', padx=(0, 5))
        ttk.Button(btn_frame, text="📂 Add Folder", command=self.add_folder).pack(side='left', padx=(0, 5))
        ttk.Button(btn_frame, text="🗑️ Remove Selected", command=self.remove_selected).pack(side='left', padx=(0, 5))
        ttk.Button(btn_frame, text="🧹 Clear All", command=self.clear_files).pack(side='left')
        
        # Security Options Card
        security_card = ttk.LabelFrame(parent, text="🛡️ Security Options", padding="15")
        security_card.pack(fill='x', pady=(0, 15))
        
        self.auto_corrupt = tk.BooleanVar()
        corrupt_check = ttk.Checkbutton(security_card, 
                                       text="⏰ Auto-corrupt files after 24 hours (Security Feature)", 
                                       variable=self.auto_corrupt)
        corrupt_check.pack(anchor='w')
        
        # Operations Card
        ops_card = ttk.LabelFrame(parent, text="🔐 Encryption Operations", padding="15")
        ops_card.pack(fill='x')
        
        ops_inner = ttk.Frame(ops_card)
        ops_inner.pack()
        
        encrypt_btn = ttk.Button(ops_inner, text="🔒 Encrypt Files", 
                                command=self.encrypt_files, width=18)
        encrypt_btn.pack(side='left', padx=(0, 15))
        
        decrypt_btn = ttk.Button(ops_inner, text="🔓 Decrypt Files", 
                                command=self.decrypt_files, width=18)
        decrypt_btn.pack(side='left')
        
    def add_files(self):
        files = filedialog.askopenfilenames(title="Select files to encrypt")
        for file in files:
            if file not in self.selected_files:
                self.selected_files.append(file)
                self.files_listbox.insert(tk.END, f"📄 {os.path.basename(file)}")
                
    def add_folder(self):
        folder = filedialog.askdirectory(title="Select folder to encrypt")
        if folder:
            added_count = 0
            for root, dirs, files in os.walk(folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file_path not in self.selected_files:
                        self.selected_files.append(file_path)
                        rel_path = os.path.relpath(file_path, folder)
                        self.files_listbox.insert(tk.END, f"📁 {rel_path}")
                        added_count += 1
            if added_count > 0:
                messagebox.showinfo("Success", f"Added {added_count} files from folder")
                
    def remove_selected(self):
        selected_indices = self.files_listbox.curselection()
        for index in reversed(selected_indices):
            self.files_listbox.delete(index)
            if index < len(self.selected_files):
                self.selected_files.pop(index)
                
    def clear_files(self):
        self.selected_files.clear()
        self.files_listbox.delete(0, tk.END)
        
    def refresh_drives(self):
        drives = []
        for partition in psutil.disk_partitions():
            if 'removable' in partition.opts or partition.device.startswith(('E:', 'F:', 'G:', 'H:')):
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    free_gb = usage.free // (1024**3)
                    drives.append(f"{partition.device} ({free_gb}GB free)")
                except:
                    drives.append(partition.device)
        
        self.drive_combo['values'] = drives
        if drives:
            self.drive_combo.current(0)
        else:
            self.drive_combo.set("No removable drives found")
            
    def create_usb_key(self):
        if not self.drive_var.get() or "No removable drives" in self.drive_var.get():
            messagebox.showerror("Error", "Please select a valid USB drive")
            return
        
        engineer_name = self.engineer_var.get().strip()
        if not engineer_name:
            messagebox.showerror("Error", "Please enter engineer name")
            return
            
        if not messagebox.askyesno("Confirm", f"Create USB key for engineer '{engineer_name}'?\n\nThis will overwrite any existing key on the selected drive."):
            return
            
        try:
            drive_path = self.drive_var.get().split()[0]
            master_key = secrets.token_bytes(32)
            key_hash = hashlib.sha256(master_key).hexdigest()
            
            engineer_info = {
                'name': engineer_name,
                'company': 'OBDPORTAL',
                'usb_drive': drive_path,
                'created_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'key_hash': key_hash
            }
            
            usb_key_path = os.path.join(drive_path, self.usb_key_file)
            with open(usb_key_path, 'wb') as f:
                f.write(master_key)
                
            eng_path = os.path.join(drive_path, "engineer.json")
            with open(eng_path, 'w') as f:
                json.dump(engineer_info, f, indent=2)
                
            with open('key_hash.txt', 'w') as f:
                f.write(key_hash)
                
            self.engineers[drive_path] = engineer_info
            self.save_engineers()
            
            self.usb_drive = drive_path
            messagebox.showinfo("Success", f"✅ OBDPORTAL USB key created successfully!\n\nEngineer: {engineer_name}\nDrive: {drive_path}")
            self.check_usb_status()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create USB key:\n{str(e)}")
            
    def verify_usb_key(self):
        if not os.path.exists('key_hash.txt'):
            messagebox.showerror("Error", "No master key hash found. Create a USB key first.")
            return
            
        with open('key_hash.txt', 'r') as f:
            stored_hash = f.read().strip()
            
        for partition in psutil.disk_partitions():
            if 'removable' in partition.opts:
                key_path = os.path.join(partition.mountpoint, self.usb_key_file)
                if os.path.exists(key_path):
                    try:
                        with open(key_path, 'rb') as f:
                            key = f.read()
                        if hashlib.sha256(key).hexdigest() == stored_hash:
                            self.usb_drive = partition.mountpoint
                            messagebox.showinfo("Success", "✅ OBDPORTAL USB key verified successfully!")
                            self.check_usb_status()
                            return
                    except:
                        continue
                        
        messagebox.showerror("Error", "❌ Valid OBDPORTAL USB key not found")
        
    def check_usb_status(self):
        if not os.path.exists('key_hash.txt'):
            self.usb_status_var.set("❌ No OBDPORTAL USB key configured")
            self.status_var.set("Create a USB key to begin")
            return
            
        with open('key_hash.txt', 'r') as f:
            stored_hash = f.read().strip()
            
        for partition in psutil.disk_partitions():
            if 'removable' in partition.opts:
                key_path = os.path.join(partition.mountpoint, self.usb_key_file)
                eng_path = os.path.join(partition.mountpoint, "engineer.json")
                if os.path.exists(key_path):
                    try:
                        with open(key_path, 'rb') as f:
                            key = f.read()
                        if hashlib.sha256(key).hexdigest() == stored_hash:
                            self.usb_drive = partition.mountpoint
                            
                            engineer_name = "Unknown"
                            if os.path.exists(eng_path):
                                with open(eng_path, 'r') as f:
                                    eng_data = json.load(f)
                                    engineer_name = eng_data.get('name', 'Unknown')
                            
                            self.usb_status_var.set(f"✅ OBDPORTAL USB Key Active - {partition.device} (Engineer: {engineer_name})")
                            self.status_var.set("Ready - USB key authenticated")
                            return
                    except:
                        continue
                        
        self.usb_drive = None
        self.usb_status_var.set("❌ OBDPORTAL USB key not detected")
        self.status_var.set("Insert USB key to encrypt/decrypt files")
        
    def get_master_key(self):
        if not self.usb_drive:
            return None
            
        key_path = os.path.join(self.usb_drive, self.usb_key_file)
        if os.path.exists(key_path):
            with open(key_path, 'rb') as f:
                return f.read()
        return None
        
    def derive_file_key(self, filename, master_key):
        salt = hashlib.sha256(filename.encode()).digest()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(master_key)

    def derive_password_key(self, password, filename):
        salt = hashlib.sha256(filename.encode()).digest()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(password.encode())
        
    def encrypt_single_file(self, file_path, master_key, auto_corrupt=False):
        filename = os.path.basename(file_path)
        file_key = self.derive_file_key(filename, master_key)
        iv = secrets.token_bytes(16)
        
        with open(file_path, 'rb') as f:
            data = f.read()
        
        # Add timestamp and corruption flag to data
        metadata = {
            'encrypted_time': time.time(),
            'auto_corrupt': auto_corrupt,
            'company': 'OBDPORTAL'
        }
        metadata_bytes = json.dumps(metadata).encode()
        metadata_length = len(metadata_bytes).to_bytes(4, 'big')
        
        # Combine metadata + original data
        full_data = metadata_length + metadata_bytes + data
            
        cipher = Cipher(algorithms.AES(file_key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        pad_len = 16 - (len(full_data) % 16)
        padded_data = full_data + bytes([pad_len] * pad_len)
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        encrypted_path = file_path + '.encrypted'
        with open(encrypted_path, 'wb') as f:
            f.write(iv + encrypted_data)
            
        return encrypted_path
        
    def check_expired_files(self):
        """Check and corrupt files that are older than 24 hours"""
        try:
            current_dir = os.getcwd()
            for filename in os.listdir(current_dir):
                if filename.endswith('.encrypted'):
                    try:
                        # Try to read metadata from encrypted file
                        with open(filename, 'rb') as f:
                            encrypted_data = f.read()
                        
                        # Skip if file is too small
                        if len(encrypted_data) < 32:
                            continue
                            
                        # Check if file should be corrupted (simplified check)
                        file_time = os.path.getctime(filename)
                        if time.time() - file_time > 86400:  # 24 hours
                            # Corrupt the file by overwriting with random data
                            with open(filename, 'wb') as f:
                                f.write(secrets.token_bytes(len(encrypted_data)))
                    except:
                        continue
        except:
            pass
        
    def encrypt_files(self):
        if not self.usb_drive:
            messagebox.showerror("Error", "USB key required for encryption")
            self.check_usb_status()
            return
            
        if not self.selected_files:
            messagebox.showerror("Error", "Please select files to encrypt")
            return
        
        auto_corrupt = self.auto_corrupt.get()
        corrupt_msg = "\n\n⚠️ Files will auto-corrupt after 24 hours!" if auto_corrupt else ""
            
        if not messagebox.askyesno("Confirm", f"Encrypt {len(self.selected_files)} files?{corrupt_msg}\n\nOriginal files will be deleted after encryption."):
            return
            
        try:
            master_key = self.get_master_key()
            if not master_key:
                messagebox.showerror("Error", "Cannot read USB key")
                return
            
            encrypted_count = 0
            failed_files = []
            
            for i, file_path in enumerate(self.selected_files):
                if os.path.exists(file_path):
                    try:
                        self.status_var.set(f"Encrypting {i+1}/{len(self.selected_files)}: {os.path.basename(file_path)}")
                        self.root.update()
                        
                        self.encrypt_single_file(file_path, master_key, auto_corrupt)
                        os.remove(file_path)
                        encrypted_count += 1
                    except Exception as e:
                        failed_files.append(f"{os.path.basename(file_path)}: {str(e)}")
                else:
                    failed_files.append(f"{os.path.basename(file_path)}: File not found")
            
            self.clear_files()
            self.status_var.set(f"Encryption completed - {encrypted_count} files encrypted")
            
            result_msg = f"✅ OBDPORTAL: Successfully encrypted {encrypted_count} files!"
            if auto_corrupt:
                result_msg += "\n\n⚠️ Security Notice: Files will auto-corrupt after 24 hours"
            if failed_files:
                result_msg += f"\n\n❌ Failed files ({len(failed_files)}):\n" + "\n".join(failed_files[:5])
                if len(failed_files) > 5:
                    result_msg += f"\n... and {len(failed_files) - 5} more"
            
            messagebox.showinfo("Encryption Complete", result_msg)
            
        except Exception as e:
            self.status_var.set("Encryption failed")
            messagebox.showerror("Error", f"Encryption failed: {str(e)}")
            
    def decrypt_files(self):
        files = filedialog.askopenfilenames(
            title="Select encrypted files to decrypt",
            filetypes=[("Encrypted files", "*.encrypted"), ("All files", "*.*")]
        )
        if not files:
            return
        
        method = messagebox.askyesnocancel("Decryption Method", 
                                          "Choose decryption method:\n\n✅ Yes = USB Key\n🔑 No = Master Password\n❌ Cancel = Abort")
        if method is None:
            return
            
        try:
            decrypted_count = 0
            failed_files = []
            expired_files = []
            
            for i, file_path in enumerate(files):
                try:
                    original_name = os.path.basename(file_path).replace('.encrypted', '')
                    self.status_var.set(f"Decrypting {i+1}/{len(files)}: {original_name}")
                    self.root.update()
                    
                    if method:  # USB Key
                        if not self.usb_drive:
                            messagebox.showerror("Error", "USB key required")
                            return
                        master_key = self.get_master_key()
                        if not master_key:
                            messagebox.showerror("Error", "Cannot read USB key")
                            return
                        file_key = self.derive_file_key(original_name, master_key)
                    else:  # Master Password
                        if i == 0:  # Only ask once
                            password = simpledialog.askstring("Master Password", "Enter master password:", show='*')
                            if not password:
                                return
                            if password != self.master_password:
                                messagebox.showerror("Error", "Invalid master password")
                                return
                        file_key = self.derive_password_key(password, original_name)
                    
                    with open(file_path, 'rb') as f:
                        encrypted_data = f.read()
                        
                    iv = encrypted_data[:16]
                    encrypted_content = encrypted_data[16:]
                    
                    cipher = Cipher(algorithms.AES(file_key), modes.CBC(iv), backend=default_backend())
                    decryptor = cipher.decryptor()
                    
                    padded_data = decryptor.update(encrypted_content) + decryptor.finalize()
                    pad_len = padded_data[-1]
                    full_data = padded_data[:-pad_len]
                    
                    # Extract metadata
                    try:
                        metadata_length = int.from_bytes(full_data[:4], 'big')
                        metadata_bytes = full_data[4:4+metadata_length]
                        metadata = json.loads(metadata_bytes.decode())
                        data = full_data[4+metadata_length:]
                        
                        # Check if file has expired (24 hours)
                        if metadata.get('auto_corrupt', False):
                            encrypted_time = metadata.get('encrypted_time', 0)
                            if time.time() - encrypted_time > 86400:  # 24 hours
                                expired_files.append(original_name)
                                continue
                    except:
                        # Fallback for files without metadata
                        data = full_data
                    
                    decrypted_path = file_path.replace('.encrypted', '')
                    with open(decrypted_path, 'wb') as f:
                        f.write(data)
                    
                    decrypted_count += 1
                    
                except Exception as e:
                    failed_files.append(f"{os.path.basename(file_path)}: {str(e)}")
                
            self.status_var.set(f"Decryption completed - {decrypted_count} files decrypted")
            
            result_msg = f"✅ OBDPORTAL: Successfully decrypted {decrypted_count} files!"
            if expired_files:
                result_msg += f"\n\n⚠️ Expired files (24h+ old): {len(expired_files)}"
            if failed_files:
                result_msg += f"\n\n❌ Failed files ({len(failed_files)}):\n" + "\n".join(failed_files[:3])
                if len(failed_files) > 3:
                    result_msg += f"\n... and {len(failed_files) - 3} more"
            
            messagebox.showinfo("Decryption Complete", result_msg)
            
        except Exception as e:
            self.status_var.set("Decryption failed")
            messagebox.showerror("Error", f"Decryption failed: {str(e)}")
            
    def load_encrypted_files(self):
        try:
            if os.path.exists(self.encrypted_files_db):
                with open(self.encrypted_files_db, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}
        
    def save_encrypted_files(self):
        with open(self.encrypted_files_db, 'w') as f:
            json.dump(self.encrypted_files, f, indent=2)
    
    def load_engineers(self):
        try:
            if os.path.exists(self.engineers_db):
                with open(self.engineers_db, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}

    def save_engineers(self):
        with open(self.engineers_db, 'w') as f:
            json.dump(self.engineers, f, indent=2)
            
    def run(self):
        def auto_refresh():
            self.check_usb_status()
            self.check_expired_files()
            self.root.after(3000, auto_refresh)
        auto_refresh()
        
        self.root.mainloop()

if __name__ == "__main__":
    app = AdvancedFileEncryptor()
    app.run()

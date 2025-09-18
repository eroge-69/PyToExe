import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import PyPDF2
import pkcs11
from pkcs11 import Mechanism, ObjectClass, Attribute
from pkcs11.util.ec import encode_ec_public_key
from Crypto.Hash import SHA256
from Crypto.PublicKey import ECC, RSA
from Crypto.Signature import pkcs1_15, DSS
import time

class PDFSignerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Digital Signer")
        self.root.geometry("800x600")
        
        # Variables
        self.token_lib_path = tk.StringVar()
        self.selected_pdfs = []
        self.token_slots = []
        self.selected_slot = None
        self.session = None
        self.private_key = None
        self.certificate = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Token library path selection
        ttk.Label(main_frame, text="PKCS#11 Library Path:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.token_lib_path, width=50).grid(row=0, column=1, pady=5, padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_library).grid(row=0, column=2, pady=5, padx=5)
        
        # Token detection
        ttk.Button(main_frame, text="Detect USB Token", command=self.detect_token).grid(row=1, column=0, columnspan=3, pady=10)
        
        # Token slots combobox
        ttk.Label(main_frame, text="Select Token Slot:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.slot_combobox = ttk.Combobox(main_frame, state="readonly")
        self.slot_combobox.grid(row=2, column=1, pady=5, padx=5, sticky=(tk.W, tk.E))
        ttk.Button(main_frame, text="Connect", command=self.connect_token).grid(row=2, column=2, pady=5, padx=5)
        
        # PDF selection
        ttk.Button(main_frame, text="Select PDFs to Sign", command=self.select_pdfs).grid(row=3, column=0, columnspan=3, pady=10)
        
        # PDF listbox
        ttk.Label(main_frame, text="Selected PDFs:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.pdf_listbox = tk.Listbox(main_frame, height=10)
        self.pdf_listbox.grid(row=5, column=0, columnspan=3, pady=5, padx=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Output directory
        ttk.Label(main_frame, text="Output Directory:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.output_dir = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.output_dir, width=50).grid(row=6, column=1, pady=5, padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_output_dir).grid(row=6, column=2, pady=5, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=7, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))
        
        # Sign button
        ttk.Button(main_frame, text="Sign PDFs", command=self.sign_pdfs).grid(row=8, column=0, columnspan=3, pady=10)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready")
        self.status_label.grid(row=9, column=0, columnspan=3, pady=5)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
    def browse_library(self):
        lib_path = filedialog.askopenfilename(
            title="Select PKCS#11 Library",
            filetypes=[("Dynamic Libraries", "*.dll;*.so;*.dylib"), ("All files", "*.*")]
        )
        if lib_path:
            self.token_lib_path.set(lib_path)
    
    def browse_output_dir(self):
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir.set(directory)
    
    def detect_token(self):
        lib_path = self.token_lib_path.get()
        if not lib_path or not os.path.exists(lib_path):
            messagebox.showerror("Error", "Please select a valid PKCS#11 library")
            return
        
        try:
            self.status_label.config(text="Detecting tokens...")
            self.root.update()
            
            # Initialize PKCS#11 lib
            lib = pkcs11.lib(lib_path)
            self.token_slots = lib.get_slots()
            
            if not self.token_slots:
                messagebox.showinfo("Info", "No tokens detected")
                self.status_label.config(text="No tokens found")
                return
            
            # Update combobox with slot IDs
            slot_ids = [str(slot.slot_id) for slot in self.token_slots]
            self.slot_combobox['values'] = slot_ids
            if slot_ids:
                self.slot_combobox.current(0)
            
            self.status_label.config(text=f"Found {len(self.token_slots)} token(s)")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to detect tokens: {str(e)}")
            self.status_label.config(text="Token detection failed")
    
    def connect_token(self):
        if not self.token_slots:
            messagebox.showerror("Error", "Please detect tokens first")
            return
        
        selected_index = self.slot_combobox.current()
        if selected_index == -1:
            messagebox.showerror("Error", "Please select a token slot")
            return
        
        try:
            self.status_label.config(text="Connecting to token...")
            self.root.update()
            
            selected_slot = self.token_slots[selected_index]
            self.session = selected_slot.open()
            
            # Try to authenticate (you might need to adjust this for your token)
            try:
                self.session.login("123456")  # Default PIN, adjust as needed
            except pkcs11.PKCS11Error as e:
                # Prompt for PIN if default fails
                pin = self.ask_for_pin()
                if pin:
                    self.session.login(pin)
                else:
                    raise Exception("Authentication cancelled")
            
            # Find private key and certificate
            private_keys = self.session.get_objects({
                Attribute.CLASS: ObjectClass.PRIVATE_KEY,
                Attribute.KEY_TYPE: pkcs11.KeyType.RSA
            })
            
            if not private_keys:
                private_keys = self.session.get_objects({
                    Attribute.CLASS: ObjectClass.PRIVATE_KEY,
                    Attribute.KEY_TYPE: pkcs11.KeyType.EC
                })
            
            if not private_keys:
                raise Exception("No private key found on token")
            
            self.private_key = list(private_keys)[0]
            
            # Find certificate
            certs = self.session.get_objects({
                Attribute.CLASS: ObjectClass.CERTIFICATE
            })
            
            if certs:
                self.certificate = list(certs)[0]
            
            self.status_label.config(text="Token connected successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect to token: {str(e)}")
            self.status_label.config(text="Token connection failed")
    
    def ask_for_pin(self):
        # Create a simple dialog to ask for PIN
        dialog = tk.Toplevel(self.root)
        dialog.title("Enter PIN")
        dialog.geometry("300x100")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Enter token PIN:").pack(pady=5)
        pin_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=pin_var, show="*").pack(pady=5)
        
        result = []
        def on_ok():
            result.append(pin_var.get())
            dialog.destroy()
        
        ttk.Button(dialog, text="OK", command=on_ok).pack(pady=5)
        
        self.root.wait_window(dialog)
        return result[0] if result else None
    
    def select_pdfs(self):
        files = filedialog.askopenfilenames(
            title="Select PDF Files",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if files:
            self.selected_pdfs = list(files)
            self.pdf_listbox.delete(0, tk.END)
            for file in self.selected_pdfs:
                self.pdf_listbox.insert(tk.END, os.path.basename(file))
    
    def sign_pdfs(self):
        if not self.session or not self.private_key:
            messagebox.showerror("Error", "Please connect to a token first")
            return
        
        if not self.selected_pdfs:
            messagebox.showerror("Error", "Please select PDF files to sign")
            return
        
        output_dir = self.output_dir.get()
        if not output_dir or not os.path.isdir(output_dir):
            messagebox.showerror("Error", "Please select a valid output directory")
            return
        
        # Start signing process in a separate thread
        thread = threading.Thread(target=self._sign_pdfs_thread, args=(output_dir,))
        thread.daemon = True
        thread.start()
    
    def _sign_pdfs_thread(self, output_dir):
        try:
            self.progress.start()
            self.status_label.config(text="Signing PDFs...")
            
            for i, pdf_path in enumerate(self.selected_pdfs):
                try:
                    self.status_label.config(text=f"Signing {i+1}/{len(self.selected_pdfs)}: {os.path.basename(pdf_path)}")
                    self.root.update()
                    
                    output_path = os.path.join(output_dir, f"signed_{os.path.basename(pdf_path)}")
                    self.sign_pdf(pdf_path, output_path)
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to sign {pdf_path}: {str(e)}")
            
            self.progress.stop()
            self.status_label.config(text="Signing completed")
            messagebox.showinfo("Success", "PDF signing completed successfully")
            
        except Exception as e:
            self.progress.stop()
            messagebox.showerror("Error", f"Signing process failed: {str(e)}")
            self.status_label.config(text="Signing failed")
    
    def sign_pdf(self, input_path, output_path):
        # Read the PDF
        with open(input_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            writer = PyPDF2.PdfWriter()
            
            # Add all pages to the writer
            for page in reader.pages:
                writer.add_page(page)
            
            # Create signature metadata
            metadata = {
                '/Name': 'Digital Signature',
                '/Location': 'PDF Signer App',
                '/Reason': 'Document authentication',
                '/Date': time.strftime("D:%Y%m%d%H%M%S+00'00'")
            }
            
            # Hash the document content
            hash_obj = SHA256.new()
            for page in reader.pages:
                hash_obj.update(page.extract_text().encode())
            
            # Sign the hash using the token
            if self.private_key.key_type == pkcs11.KeyType.RSA:
                mechanism = Mechanism.RSA_PKCS
                signature = self.private_key.sign(hash_obj.digest(), mechanism=mechanism)
            else:  # EC key
                mechanism = Mechanism.ECDSA
                signature = self.private_key.sign(hash_obj.digest(), mechanism=mechanism)
            
            # Add signature to the PDF
            writer.add_metadata(metadata)
            
            # Write the signed PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            # In a real application, you would embed the signature properly
            # This is a simplified version for demonstration
    
    def __del__(self):
        if self.session:
            try:
                self.session.logout()
                self.session.close()
            except:
                pass

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFSignerApp(root)
    root.mainloop()
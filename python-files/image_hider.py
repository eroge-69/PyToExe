import argparse
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256
import base64
import tkinter as tk
from tkinter import filedialog, messagebox
import hashlib
import os

class AESCipher:
    def __init__(self, key):
        self.key = key

    def encrypt(self, plaintext):
        cipher = AES.new(self.key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(plaintext.encode('utf-8'), AES.block_size))
        iv = base64.b64encode(cipher.iv).decode('utf-8')
        ct = base64.b64encode(ct_bytes).decode('utf-8')
        return iv + ct

    def decrypt(self, ciphertext):
        iv = base64.b64decode(ciphertext[:24])
        ct = base64.b64decode(ciphertext[24:])
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        return pt.decode('utf-8')

def generate_key():
    return get_random_bytes(16)

def generate_key_from_password(password, salt=None):
    if salt is None:
        salt = get_random_bytes(16)
    key = PBKDF2(password, salt, 16, count=100000, hmac_hash_module=SHA256)
    return key, salt

def save_key(key, filename):
    with open(filename, 'wb') as f:
        f.write(key)

def load_key(filename):
    with open(filename, 'rb') as f:
        return f.read()

def embed_text_in_image(image_path, text, password=None, key=None, output_path=None):
    """Embed encrypted text after the image hex data"""
    if not password and not key:
        raise ValueError("Either password or key must be provided")
    
    # Read the original image
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    # Generate key from password or use provided key
    if password:
        encryption_key, salt = generate_key_from_password(password)
    else:
        encryption_key = key
        salt = None
    
    # Encrypt the text
    cipher = AESCipher(encryption_key)
    encrypted_text = cipher.encrypt(text)
    
    # Create marker to identify embedded data
    marker = b"ENCRYPTED_TEXT_START"
    
    # Prepare the data to append
    embedded_data = marker
    if salt:
        embedded_data += b"SALT:" + base64.b64encode(salt) + b"\n"
    embedded_data += b"DATA:" + encrypted_text.encode('utf-8')
    
    # Write new image with embedded data
    if not output_path:
        name, ext = os.path.splitext(image_path)
        output_path = f"{name}_with_text{ext}"
    
    with open(output_path, 'wb') as f:
        f.write(image_data)
        f.write(embedded_data)
    
    return output_path

def extract_text_from_image(image_path, password=None, key=None):
    """Extract and decrypt text from image"""
    if not password and not key:
        raise ValueError("Either password or key must be provided")
    
    with open(image_path, 'rb') as f:
        data = f.read()
    
    # Find the marker
    marker = b"ENCRYPTED_TEXT_START"
    marker_pos = data.find(marker)
    
    if marker_pos == -1:
        raise ValueError("No embedded text found in image")
    
    # Extract embedded data
    embedded_data = data[marker_pos + len(marker):]
    embedded_str = embedded_data.decode('utf-8', errors='ignore')
    
    salt = None
    encrypted_text = None
    
    # Parse the embedded data
    lines = embedded_str.split('\n')
    for line in lines:
        if line.startswith('SALT:'):
            salt = base64.b64decode(line[5:])
        elif line.startswith('DATA:'):
            encrypted_text = line[5:]
    
    if not encrypted_text:
        raise ValueError("Invalid embedded data format")
    
    # Generate key if password provided
    if password:
        if not salt:
            raise ValueError("Salt not found but password provided")
        encryption_key, _ = generate_key_from_password(password, salt)
    else:
        encryption_key = key
    
    # Decrypt the text
    cipher = AESCipher(encryption_key)
    decrypted_text = cipher.decrypt(encrypted_text)
    
    return decrypted_text

class GUI:
    def __init__(self, master):
        self.master = master
        master.title("Image Text Embedder - AES Encryption")
        master.geometry("600x700")

        # Text encryption section
        tk.Label(master, text="Text Encryption/Decryption", font=("Arial", 14, "bold")).pack(pady=10)
        
        tk.Label(master, text="Enter text:").pack()
        self.text_entry = tk.Entry(master, width=50)
        self.text_entry.pack(pady=5)

        button_frame1 = tk.Frame(master)
        button_frame1.pack(pady=5)
        
        tk.Button(button_frame1, text="Encrypt", command=self.encrypt).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame1, text="Decrypt", command=self.decrypt).pack(side=tk.LEFT, padx=5)

        tk.Label(master, text="Result:").pack()
        self.result_text = tk.Text(master, height=5, width=70)
        self.result_text.pack(pady=5)

        # Image embedding section
        tk.Label(master, text="Image Text Embedding", font=("Arial", 14, "bold")).pack(pady=(20, 10))
        
        tk.Label(master, text="Text to embed:").pack()
        self.embed_text = tk.Text(master, height=3, width=70)
        self.embed_text.pack(pady=5)
        
        tk.Label(master, text="Password (optional - leave empty to use key file):").pack()
        self.password_entry = tk.Entry(master, width=50, show="*")
        self.password_entry.pack(pady=5)

        button_frame2 = tk.Frame(master)
        button_frame2.pack(pady=10)
        
        tk.Button(button_frame2, text="Select Image & Embed Text", command=self.embed_text_in_image).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame2, text="Select Image & Extract Text", command=self.extract_text_from_image).pack(side=tk.LEFT, padx=5)

        tk.Label(master, text="Extracted/Status:").pack()
        self.status_text = tk.Text(master, height=5, width=70)
        self.status_text.pack(pady=5)

        self.key = None
        self.cipher = None

    def load_key(self):
        key_file = 'aes_key.bin'
        try:
            self.key = load_key(key_file)
            self.cipher = AESCipher(self.key)
        except FileNotFoundError:
            self.key = generate_key()
            save_key(self.key, key_file)
            self.cipher = AESCipher(self.key)

    def encrypt(self):
        self.load_key()
        plaintext = self.text_entry.get()
        ciphertext = self.cipher.encrypt(plaintext)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, ciphertext)

    def decrypt(self):
        self.load_key()
        ciphertext = self.text_entry.get()
        try:
            plaintext = self.cipher.decrypt(ciphertext)
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, plaintext)
        except (ValueError, KeyError):
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "Decryption failed. Invalid ciphertext or key.")

    def embed_text_in_image(self):
        image_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff")]
        )
        
        if not image_path:
            return
        
        text_to_embed = self.embed_text.get(1.0, tk.END).strip()
        if not text_to_embed:
            messagebox.showerror("Error", "Please enter text to embed")
            return
        
        password = self.password_entry.get().strip()
        
        try:
            if password:
                output_path = embed_text_in_image(image_path, text_to_embed, password=password)
            else:
                self.load_key()
                output_path = embed_text_in_image(image_path, text_to_embed, key=self.key)
            
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(tk.END, f"Text successfully embedded in: {output_path}")
            messagebox.showinfo("Success", f"Text embedded successfully!\nOutput: {output_path}")
            
        except Exception as e:
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(tk.END, f"Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to embed text: {str(e)}")

    def extract_text_from_image(self):
        image_path = filedialog.askopenfilename(
            title="Select Image with Embedded Text",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff")]
        )
        
        if not image_path:
            return
        
        password = self.password_entry.get().strip()
        
        try:
            if password:
                extracted_text = extract_text_from_image(image_path, password=password)
            else:
                self.load_key()
                extracted_text = extract_text_from_image(image_path, key=self.key)
            
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(tk.END, f"Extracted text:\n{extracted_text}")
            
        except Exception as e:
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(tk.END, f"Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to extract text: {str(e)}")

root = tk.Tk()
gui = GUI(root)
root.mainloop()
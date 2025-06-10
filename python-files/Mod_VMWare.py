import os
import psutil
import tkinter as tk
from tkinter import messagebox
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
import base64
import getpass
import subprocess
import json

# Configuración de la clave de cifrado (usamos un valor fijo + SID del usuario para generar la clave)
def get_secret_key():
    # Tomamos un valor fijo para la clave + SID del usuario (puede personalizarse)
    user_sid = os.environ.get("USERPROFILE", "")
    secret_key = PBKDF2(user_sid, b"salt", dkLen=32)  # AES-256
    return secret_key

# Cifrar la contraseña
def encrypt_password(password):
    secret_key = get_secret_key()
    cipher = AES.new(secret_key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(password.encode())
    nonce = base64.b64encode(cipher.nonce).decode('utf-8')
    ciphertext_b64 = base64.b64encode(ciphertext).decode('utf-8')
    return json.dumps({"nonce": nonce, "ciphertext": ciphertext_b64, "tag": base64.b64encode(tag).decode('utf-8')})

# Descifrar la contraseña
def decrypt_password(encrypted_password):
    secret_key = get_secret_key()
    data = json.loads(encrypted_password)
    nonce = base64.b64decode(data["nonce"])
    ciphertext = base64.b64decode(data["ciphertext"])
    tag = base64.b64decode(data["tag"])

    cipher = AES.new(secret_key, AES.MODE_GCM, nonce=nonce)
    password = cipher.decrypt_and_verify(ciphertext, tag)
    return password.decode()

# Detectar adaptadores de VMware
def get_vmware_adapters():
    adapters = []
    for nic, addrs in psutil.net_if_addrs().items():
        if "VMware" in nic:
            adapters.append(nic)
    return adapters

# Ejecutar comando como administrador (elevación de privilegios)
def run_as_admin(command):
    try:
        subprocess.run(f'runas /user:Administrator "{command}"', check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error ejecutando el comando: {e}")

# Modificar configuración de red de VMware
def modify_adapter(adapter_name, ip, subnet, gateway):
    command = f'netsh interface ip set address "{adapter_name}" static {ip} {subnet} {gateway}'
    run_as_admin(command)

# Función para guardar la contraseña cifrada
def save_password(encrypted_password):
    with open("admin_password.json", "w") as f:
        f.write(encrypted_password)

# Función para cargar la contraseña cifrada
def load_password():
    if os.path.exists("admin_password.json"):
        with open("admin_password.json", "r") as f:
            return f.read()
    return None

# Interfaz gráfica
class VMwareNetworkConfigurator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("VMware Network Configurator")
        self.geometry("400x300")

        self.password = load_password()
        self.init_ui()

    def init_ui(self):
        self.adapter_label = tk.Label(self, text="Selecciona el adaptador VMware:")
        self.adapter_label.pack(pady=10)

        self.adapters = get_vmware_adapters()
        self.adapter_var = tk.StringVar(value=self.adapters[0] if self.adapters else "No VMware adapters found")
        self.adapter_dropdown = tk.OptionMenu(self, self.adapter_var, *self.adapters)
        self.adapter_dropdown.pack(pady=10)

        self.ip_label = tk.Label(self, text="IP:")
        self.ip_label.pack()
        self.ip_entry = tk.Entry(self)
        self.ip_entry.pack()

        self.subnet_label = tk.Label(self, text="Subred:")
        self.subnet_label.pack()
        self.subnet_entry = tk.Entry(self)
        self.subnet_entry.pack()

        self.gateway_label = tk.Label(self, text="Puerta de enlace:")
        self.gateway_label.pack()
        self.gateway_entry = tk.Entry(self)
        self.gateway_entry.pack()

        self.save_button = tk.Button(self, text="Guardar Configuración", command=self.save_configuration)
        self.save_button.pack(pady=10)

        if not self.password:
            self.password_button = tk.Button(self, text="Ingresar Contraseña Admin", command=self.enter_password)
            self.password_button.pack(pady=10)

    def enter_password(self):
        def submit_password():
            password = password_entry.get()
            encrypted_password = encrypt_password(password)
            save_password(encrypted_password)
            self.password = encrypted_password
            password_window.destroy()
            messagebox.showinfo("Éxito", "Contraseña guardada con éxito.")

        password_window = tk.Toplevel(self)
        password_window.title("Ingrese la Contraseña de Administrador")

        password_label = tk.Label(password_window, text="Contraseña:")
        password_label.pack(pady=10)

        password_entry = tk.Entry(password_window, show="*")
        password_entry.pack(pady=10)

        submit_button = tk.Button(password_window, text="Guardar", command=submit_password)
        submit_button.pack(pady=10)

    def save_configuration(self):
        adapter = self.adapter_var.get()
        ip = self.ip_entry.get()
        subnet = self.subnet_entry.get()
        gateway = self.gateway_entry.get()

        # Verifica si la contraseña está cargada y luego modifica el adaptador
        if self.password:
            decrypted_password = decrypt_password(self.password)
            # Realiza la modificación del adaptador
            modify_adapter(adapter, ip, subnet, gateway)
            messagebox.showinfo("Configuración Guardada", "Configuración de red aplicada correctamente.")
        else:
            messagebox.showwarning("Advertencia", "Debe ingresar la contraseña de administrador primero.")

if __name__ == "__main__":
    app = VMwareNetworkConfigurator()
    app.mainloop()

import psutil
import json
import tkinter as tk
from tkinter import ttk

class IPChangerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de IPs")

        # Obtener módulos de red
        self.interfaces = self.get_network_interfaces()

        # Interfaz gráfica
        self.create_widgets()

    def get_network_interfaces(self):
        return list(psutil.net_if_addrs().keys())

    def save_config(self):
        config = {
            "selected_interface": self.interface_var.get(),
            "ip_address": self.ip_var.get()
        }
        with open("config.json", "w") as file:
            json.dump(config, file)
        print("Configuración guardada.")

    def create_widgets(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.grid(row=0, column=0)

        ttk.Label(frame, text="Módulo de red:").grid(row=0, column=0)
        self.interface_var = tk.StringVar()
        interface_menu = ttk.Combobox(frame, textvariable=self.interface_var, values=self.interfaces)
        interface_menu.grid(row=0, column=1)

        ttk.Label(frame, text="Dirección IP:").grid(row=1, column=0)
        self.ip_var = tk.StringVar()
        ip_entry = ttk.Entry(frame, textvariable=self.ip_var)
        ip_entry.grid(row=1, column=1)

        ttk.Button(frame, text="Aceptar", command=self.save_config).grid(row=2, column=0)
        ttk.Button(frame, text="Cancelar", command=self.root.quit).grid(row=2, column=1)

if __name__ == "__main__":
    root = tk.Tk()
    app = IPChangerApp(root)
    root.mainloop()


import tkinter as tk
from tkinter import ttk
import json
import os

# Path ke file config.json di folder yang sama
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {
            "server": "10.33.23.20:3000/",
            "ktprw": "10.33.23.20:38885/"
        }
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=4)

def update_display():
    cfg = load_config()
    server_port = "3001" if ":3001" in cfg["server"] else "3000"
    server_label_var.set(f"Port Server: {server_port}")
    proxy_var.set(cfg["ktprw"].split(":")[0])

def toggle_port():
    cfg = load_config()
    if ":3001" in cfg["server"]:
        cfg["server"] = cfg["server"].replace(":3001", ":3000")
    else:
        cfg["server"] = cfg["server"].replace(":3000", ":3001")
    save_config(cfg)
    update_display()

def set_proxy(val):
    cfg = load_config()
    port = cfg["ktprw"].split(":")[1] if ":" in cfg["ktprw"] else "38885"
    cfg["ktprw"] = f"{val}:{port}"
    save_config(cfg)
    update_display()

# GUI
root = tk.Tk()
root.title("Config SIAK Editor")
root.geometry("300x160")
root.resizable(False, False)

server_label_var = tk.StringVar()
proxy_var = tk.StringVar()

tk.Label(root, textvariable=server_label_var, font=("Arial", 10)).pack(pady=10)
tk.Button(root, text="Ubah Port Server (3000/3001)", command=toggle_port).pack()

tk.Label(root, text="Pilih Proxy:", font=("Arial", 10)).pack(pady=(10, 0))
proxy_choices = ["10.33.23.20", "10.33.23.24", "10.33.23.5"]
proxy_menu = ttk.Combobox(root, values=proxy_choices, textvariable=proxy_var, state="readonly")
proxy_menu.pack()
proxy_menu.bind("<<ComboboxSelected>>", lambda e: set_proxy(proxy_var.get()))

update_display()
root.mainloop()

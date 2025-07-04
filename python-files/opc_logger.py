import tkinter as tk
from tkinter import messagebox, filedialog
from opcua import Client
import pandas as pd
import threading
import time
from datetime import datetime
import json
import os
import matplotlib.pyplot as plt

TAG_PREFIX = "S7_MyPLC.PLC300."

def nacti_config(soubor="config.txt"):
    config = {
        "server": "opc.tcp://localhost:49320",
        "password": "admin123",
        "interval": 1,
        "output_format": "xlsx",
        "output_dir": os.getcwd()
    }
    if os.path.exists(soubor):
        with open(soubor, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    if key == "interval":
                        config[key] = float(value)
                    else:
                        config[key] = value
    return config

def uloz_tagy(tagy, soubor="tags.json"):
    with open(soubor, "w", encoding="utf-8") as f:
        json.dump(tagy, f)

def nacti_tagy(soubor="tags.json"):
    if os.path.exists(soubor):
        with open(soubor, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

class OPCLoggerApp:
    def __init__(self, root, config):
        self.root = root
        self.root.title("OPC Logger")

        self.config = config
        self.tags = nacti_tagy()
        self.nodes = {}
        self.client = None
        self.running = False
        self.data = []
        self.interval = config["interval"]

        self.entry = tk.Entry(root, width=50)
        self.entry.pack(pady=5)

        self.add_button = tk.Button(root, text="➕ Přidat tag", command=self.add_tag)
        self.add_button.pack()

        self.listbox = tk.Listbox(root, width=60, height=8)
        self.listbox.pack(pady=5)
        for tag in self.tags:
            self.listbox.insert(tk.END, tag)

        self.start_button = tk.Button(root, text="▶️ Start logování", command=self.start_logging)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(root, text="⏹ Stop a uložit", command=self.stop_logging)
        self.stop_button.pack(pady=5)

        self.interval_label = tk.Label(root, text="Interval logování (s):")
        self.interval_label.pack()
        self.interval_entry = tk.Entry(root, width=10)
        self.interval_entry.insert(0, str(self.interval))
        self.interval_entry.pack(pady=5)

        self.edit_button = tk.Button(root, text="✏️ Upravit vybraný tag", command=self.edit_tag)
        self.edit_button.pack(pady=2)

        self.delete_button = tk.Button(root, text="❌ Smazat vybraný tag", command=self.delete_tag)
        self.delete_button.pack(pady=2)

    def add_tag(self):
        suffix = self.entry.get().strip()
        tag = TAG_PREFIX + suffix
        if not tag.startswith(TAG_PREFIX):
            messagebox.showerror("Chybný tag", f"Tag musí začínat: {TAG_PREFIX}")
            return
        if tag:
            self.tags.append(tag)
            self.listbox.insert(tk.END, tag)
            self.entry.delete(0, tk.END)
            uloz_tagy(self.tags)

    def start_logging(self):

        try:
            self.interval = float(self.interval_entry.get())
        except ValueError:
            messagebox.showerror("Chyba", "Interval musí být číslo.")
            return
        try:
            self.client = Client(self.config["server"])
            self.client.connect()
            self.nodes = {tag: self.client.get_node(f"ns=2;s={tag}") for tag in self.tags}
            self.running = True
            self.data = []
            threading.Thread(target=self.log_loop, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Chyba připojení", str(e))

    def log_loop(self):
        while self.running:
            row = {"čas": datetime.now()}
            for tag, node in self.nodes.items():
                try:
                    row[tag] = node.get_value()
                except:
                    row[tag] = "chyba"
            self.data.append(row)
            time.sleep(self.interval)

    def stop_logging(self):
        self.running = False
        time.sleep(self.interval + 0.2)
        try:
            self.client.disconnect()
        except:
            pass

        df = pd.DataFrame(self.data)
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"OPC_Log_{now}.{self.config['output_format']}"

        os.makedirs(self.config["output_dir"], exist_ok=True)
        filepath = os.path.join(self.config["output_dir"], filename)

        if self.config["output_format"] == "csv":
            df.to_csv(filepath, index=False)
        else:
            df.to_excel(filepath, index=False)

        messagebox.showinfo("Hotovo", f"Soubor uložen:\n{filepath}")
        self.vykresli_graf(df)


    def edit_tag(self):
        try:
            index = self.listbox.curselection()[0]
            new_value = tk.simpledialog.askstring("Úprava tagu", "Zadej nový tag:", initialvalue=self.tags[index])
            if new_value:
                self.tags[index] = new_value.strip()
                self.listbox.delete(index)
                self.listbox.insert(index, new_value.strip())
                uloz_tagy(self.tags)
        except IndexError:
            messagebox.showinfo("Info", "Nejprve vyber tag ze seznamu.")

    def delete_tag(self):
        try:
            index = self.listbox.curselection()[0]
            self.listbox.delete(index)
            del self.tags[index]
            uloz_tagy(self.tags)
        except IndexError:
            messagebox.showinfo("Info", "Nejprve vyber tag ze seznamu.")
    def vykresli_graf(self, df):
        plt.figure()
        for tag in self.tags:
            if tag in df.columns:
                plt.plot(df["čas"], df[tag], label=tag)
        plt.xlabel("Čas")
        plt.ylabel("Hodnota")
        plt.legend()
        plt.title("Graf logovaných proměnných")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

def over_heslo(config):
    heslo_okno = tk.Tk()
    heslo_okno.title("Zadej heslo")

    tk.Label(heslo_okno, text="Zadej heslo pro spuštění:").pack(pady=10)
    entry = tk.Entry(heslo_okno, show="*")
    entry.pack(pady=5)

    def zkontroluj():
        if entry.get() == config["password"]:
            heslo_okno.destroy()
            root = tk.Tk()
            app = OPCLoggerApp(root, config)
            root.mainloop()
        else:
            messagebox.showerror("Chyba", "Nesprávné heslo!")

    tk.Button(heslo_okno, text="Potvrdit", command=zkontroluj).pack(pady=10)
    heslo_okno.mainloop()

config = nacti_config()
over_heslo(config)

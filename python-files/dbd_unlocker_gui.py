
import tkinter as tk
from tkinter import messagebox
import memorylib

class DBDUnlockerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DBD Unlocker Pro")
        self.root.geometry("300x150")

        self.status_label = tk.Label(root, text="Status: Not connected")
        self.status_label.pack(pady=10)

        self.connect_button = tk.Button(root, text="Connect to Dead by Daylight", command=self.connect)
        self.connect_button.pack(pady=5)

        self.unlock_button = tk.Button(root, text="Unlock All", command=self.unlock_all, state=tk.DISABLED)
        self.unlock_button.pack(pady=5)

        self.dbd_process = None

    def connect(self):
        self.status_label.config(text="Connecting...")
        self.root.update()

        try:
            self.dbd_process = memorylib.find_process("DeadByDaylight.exe")
            if self.dbd_process:
                self.status_label.config(text="Connected to Dead by Daylight")
                self.unlock_button.config(state=tk.NORMAL)
            else:
                raise Exception("Game not found. Please launch it first.")
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")
            messagebox.showerror("Error", str(e))

    def unlock_all(self):
        try:
            if not self.dbd_process:
                raise Exception("Not connected to game")

            address = self.dbd_process.scan("?? ?? 01 00 FF 01 ?? 00", offset=0x10)
            if address:
                self.dbd_process.write_memory(address, b'\xFF' * 256)  # unlock all perks
                messagebox.showinfo("Success", "Perks unlocked!")
            else:
                messagebox.showwarning("Warning", "Could not find perks address.")
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = DBDUnlockerApp(root)
    root.mainloop()

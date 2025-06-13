
import qrcode
import tkinter as tk
from tkinter import simpledialog, messagebox

def generate_qr():
    root = tk.Tk()
    root.withdraw()

    user_id = simpledialog.askstring("User Input", "Enter User ID:")
    password = simpledialog.askstring("User Input", "Enter Password:", show='*')

    if not user_id or not password:
        messagebox.showerror("Error", "Both User ID and Password are required.")
        return

    data = f"User ID:\t{user_id}\nPassword:\t{password}"

    qr = qrcode.make(data)
    qr.save("login_qr.png")

    messagebox.showinfo("Success", "QR code saved as 'login_qr.png'.")

if __name__ == "__main__":
    generate_qr()

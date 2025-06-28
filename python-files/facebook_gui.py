import tkinter as tk
from tkinter import messagebox

hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
redirect_ip = "127.0.0.1"
websites = [
    "facebook.com", "www.facebook.com", "m.facebook.com",
    "web.facebook.com", "mbasic.facebook.com",
    "login.facebook.com", "apps.facebook.com"
]

def block_facebook():
    try:
        with open(hosts_path, 'r+') as file:
            content = file.read()
            for site in websites:
                entry = f"{redirect_ip} {site}\n"
                if site not in content:
                    file.write(entry)
        messagebox.showinfo("✅ Done", "Facebook is now BLOCKED.")
    except PermissionError:
        messagebox.showerror("❌ Error", "Please run as Administrator!")

def unblock_facebook():
    try:
        with open(hosts_path, 'r+') as file:
            lines = file.readlines()
            file.seek(0)
            for line in lines:
                if not any(site in line for site in websites):
                    file.write(line)
            file.truncate()
        messagebox.showinfo("✅ Done", "Facebook is now UNBLOCKED.")
    except PermissionError:
        messagebox.showerror("❌ Error", "Please run as Administrator!")

# GUI Design
root = tk.Tk()
root.title("Facebook Blocker")
root.geometry("350x200")
root.resizable(False, False)

label = tk.Label(root, text="Facebook Blocker/Unblocker", font=("Arial", 14))
label.pack(pady=15)

block_btn = tk.Button(root, text="🚫 Block Facebook", command=block_facebook, bg="red", fg="white", font=("Arial", 12))
block_btn.pack(pady=5)

unblock_btn = tk.Button(root, text="✅ Unblock Facebook", command=unblock_facebook, bg="green", fg="white", font=("Arial", 12))
unblock_btn.pack(pady=5)

root.mainloop()


import tkinter as tk
from tkinter import ttk, messagebox
import requests

def get_subscription():
    mac = mac_entry.get().strip()
    if not mac:
        messagebox.showerror("خطأ", "يرجى إدخال قيمة MAC أو m")
        return

    url = f"http://xmobis.me/r/m.php?a=1234567800&m={mac}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.text
        output.delete("1.0", tk.END)
        output.insert(tk.END, data)
    except Exception as e:
        messagebox.showerror("خطأ في الاتصال", str(e))

def clear_all():
    mac_entry.delete(0, tk.END)
    output.delete("1.0", tk.END)

# واجهة البرنامج
root = tk.Tk()
root.title("IPTV Subscription Fetcher")
root.geometry("550x450")
root.resizable(False, False)

ttk.Label(root, text="أدخل MAC أو m:", font=("Arial", 12)).pack(pady=10)
mac_entry = ttk.Entry(root, width=40)
mac_entry.pack()

btn_frame = ttk.Frame(root)
btn_frame.pack(pady=10)
ttk.Button(btn_frame, text="Fetch Subscription", command=get_subscription).grid(row=0, column=0, padx=5)
ttk.Button(btn_frame, text="Clear", command=clear_all).grid(row=0, column=1, padx=5)

ttk.Label(root, text="Output:", font=("Arial", 12)).pack(anchor="w", padx=10)
output = tk.Text(root, wrap="word", font=("Courier", 10))
output.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

root.mainloop()

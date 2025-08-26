import tkinter as tk
from tkinter import messagebox, scrolledtext
import subprocess
import threading
import platform
import re

# DNS servers
dns_servers = {
    "Google": ("8.8.8.8", "8.8.4.4"),
    "Cloudflare": ("1.1.1.1", "1.0.0.1"),
    "OpenDNS": ("208.67.222.222", "208.67.220.220"),
    "شکن": ("185.222.222.222", "185.222.222.223"),
    "الکترو": ("103.56.207.1", "103.56.207.2"),
    "رادار گیم": ("45.77.48.25", "45.77.48.26"),
    "شلتر": ("94.130.179.10", "94.130.179.11"),
}

interface_name = "Wi-Fi"

def run_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return None

def set_dns(primary, secondary):
    try:
        subprocess.run(f'netsh interface ip set dns name="{interface_name}" static {primary}', shell=True, check=True)
        subprocess.run(f'netsh interface ip add dns name="{interface_name}" {secondary} index=2', shell=True, check=True)
        messagebox.showinfo("موفقیت", f"DNS به {primary} و {secondary} تغییر کرد!")
    except subprocess.CalledProcessError:
        messagebox.showerror("خطا", "برنامه را با دسترسی ادمین اجرا کن.")

def reset_dhcp():
    try:
        subprocess.run(f'netsh interface ip set dns name="{interface_name}" dhcp', shell=True, check=True)
        messagebox.showinfo("موفقیت", "DNS به حالت خودکار برگشت.")
    except subprocess.CalledProcessError:
        messagebox.showerror("خطا", "برنامه را با دسترسی ادمین اجرا کن.")

def ping_host(host):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    cmd = f"ping {param} 1 {host}"
    result = run_command(cmd)
    if result and ("time=" in result or "زمان=" in result):
        match = re.search(r"time[=<]\\s*(\\d+)", result)
        if not match:
            match = re.search(r"زمان[=<]\\s*(\\d+)", result)
        if match:
            return f"{match.group(1)} ms"
    return "عدم پاسخ"

def show_ping_active():
    selected = dns_listbox.curselection()
    if not selected:
        messagebox.showwarning("اخطار", "لطفاً یک DNS انتخاب کن.")
        return
    choice = dns_listbox.get(selected)
    primary, _ = dns_servers[choice]
    result = ping_host(primary)
    messagebox.showinfo("پینگ DNS فعال", f"{choice} ({primary}): {result}")

def show_ping_all():
    def do_ping():
        ping_text.config(state='normal')
        ping_text.delete(1.0, tk.END)
        for name, (primary, secondary) in dns_servers.items():
            r1 = ping_host(primary)
            r2 = ping_host(secondary)
            ping_text.insert(tk.END, f"{name}:\n  Primary: {primary} => {r1}\n  Secondary: {secondary} => {r2}\n\n")
        ping_text.config(state='disabled')

    win = tk.Toplevel(root)
    win.title("پینگ همه DNSها")
    win.geometry("450x450")
    win.config(bg="#3b005e")

    global ping_text
    ping_text = scrolledtext.ScrolledText(win, font=("Helvetica", 12), bg="#1a001f", fg="#ff005a")
    ping_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    ping_text.insert(tk.END, "در حال پینگ...\n")
    ping_text.config(state='disabled')

    threading.Thread(target=do_ping, daemon=True).start()

def on_select(event):
    selected = dns_listbox.curselection()
    if not selected:
        return
    choice = dns_listbox.get(selected)
    primary, secondary = dns_servers[choice]
    set_dns(primary, secondary)

root = tk.Tk()
root.title("تغییر دهنده DNS خفن")
root.geometry("450x450")
root.config(bg="#3b005e")

tk.Label(root, text="یک DNS انتخاب کن:", font=("Helvetica", 16, "bold"), fg="#ff005a", bg="#3b005e").pack(pady=15)

dns_listbox = tk.Listbox(root, font=("Helvetica", 14), fg="#ff005a", bg="#1a001f",
                         selectbackground="#ff005a", selectforeground="#3b005e", height=10)
for dns in dns_servers:
    dns_listbox.insert(tk.END, dns)
dns_listbox.pack(pady=10, padx=20)
dns_listbox.bind("<<ListboxSelect>>", on_select)

frame = tk.Frame(root, bg="#3b005e")
frame.pack(pady=15)

tk.Button(frame, text="بازگشت به DHCP", command=reset_dhcp, font=("Helvetica", 12, "bold"),
          bg="#ff005a", fg="#3b005e", width=15).grid(row=0, column=0, padx=10)

tk.Button(frame, text="نمایش پینگ DNS فعال", command=show_ping_active, font=("Helvetica", 12, "bold"),
          bg="#ff005a", fg="#3b005e", width=18).grid(row=0, column=1, padx=10)

tk.Button(root, text="نمایش پینگ همه DNSها", command=show_ping_all, font=("Helvetica", 12, "bold"),
          bg="#ff005a", fg="#3b005e", width=35).pack(pady=10)

root.mainloop()

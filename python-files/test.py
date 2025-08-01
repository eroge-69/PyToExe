import tkinter as tk
from ping3 import ping
from threading import Thread
import webbrowser

# ✅ قائمة الكاميرات
camera_ips = [
    '10.0.0.32', '10.0.0.33', '10.0.0.34', '10.0.0.35', '10.0.0.99',
    '10.0.101.10', '10.0.101.11', '10.0.101.12', '10.0.101.13', '10.0.101.14',
    '10.0.101.15', '10.0.101.17', '10.0.101.18', '10.0.101.19', '10.0.101.2',
    '10.0.101.20', '10.0.101.21', '10.0.101.22', '10.0.101.23', '10.0.101.24',
    '10.0.101.25', '10.0.101.26', '10.0.101.27', '10.0.101.28', '10.0.101.29',
    '10.0.101.3', '10.0.101.30', '10.0.101.31', '10.0.101.51', '10.0.101.53',
    '10.0.101.54', '10.0.101.6', '10.0.101.7', '10.0.101.8', '10.0.101.9',
    '10.0.102.1', '10.0.102.10', '10.0.102.11', '10.0.102.12', '10.0.102.13',
    '10.0.102.14', '10.0.102.15', '10.0.102.16', '10.0.102.17', '10.0.102.2',
    '10.0.102.3', '10.0.102.4', '10.0.102.5', '10.0.102.51', '10.0.102.52',
    '10.0.102.6', '10.0.102.7', '10.0.102.8', '10.0.102.9', '10.0.103.1',
    '10.0.103.10', '10.0.103.11', '10.0.103.12', '10.0.103.13', '10.0.103.14',
    '10.0.103.15', '10.0.103.16', '10.0.103.17', '10.0.103.18', '10.0.103.19',
    '10.0.103.2', '10.0.103.20', '10.0.103.21', '10.0.103.22', '10.0.103.23',
    '10.0.103.24', '10.0.103.25', '10.0.103.26', '10.0.103.27', '10.0.103.28',
    '10.0.103.29', '10.0.103.3', '10.0.103.30', '10.0.103.31', '10.0.103.32',
    '10.0.103.34', '10.0.103.35', '10.0.103.36', '10.0.103.37', '10.0.103.38',
    '10.0.103.39', '10.0.103.4', '10.0.103.51', '10.0.103.52', '10.0.103.53',
    '10.0.103.54', '10.0.103.55', '10.0.103.5', '10.0.103.6', '10.0.103.7',
    '10.0.103.8', '10.0.103.9', '10.0.104.1', '10.0.104.10', '10.0.104.11',
    '10.0.104.12', '10.0.104.13', '10.0.104.14', '10.0.104.15', '10.0.104.16',
    '10.0.104.17', '10.0.104.18', '10.0.104.19', '10.0.104.2', '10.0.104.20',
    '10.0.104.21', '10.0.104.22', '10.0.104.23', '10.0.104.24', '10.0.104.26',
    '10.0.104.27', '10.0.104.28', '10.0.104.3', '10.0.104.4', '10.0.104.51',
    '10.0.104.52', '10.0.104.7', '10.0.104.8', '10.0.104.9', '10.0.105.1',
    '10.0.105.10', '10.0.105.11', '10.0.105.12', '10.0.105.14', '10.0.105.15',
    '10.0.105.16', '10.0.105.2', '10.0.105.23', '10.0.105.24', '10.0.105.25',
    '10.0.105.27', '10.0.105.3', '10.0.105.4', '10.0.105.51', '10.0.105.9',
    '10.0.106.1', '10.0.106.10', '10.0.106.11', '10.0.106.12', '10.0.106.13',
    '10.0.106.14', '10.0.106.15', '10.0.106.16', '10.0.106.17', '10.0.106.18',
    '10.0.106.19', '10.0.106.2', '10.0.106.20', '10.0.106.21', '10.0.106.23',
    '10.0.106.24', '10.0.106.25', '10.0.106.28', '10.0.106.29', '10.0.106.3',
    '10.0.106.30', '10.0.106.4', '10.0.106.5', '10.0.106.52', '10.0.106.53',
    '10.0.106.56', '10.0.106.6', '10.0.106.7', '10.0.106.8', '10.0.106.9',
    '10.0.106.51', '10.0.107.1', '10.0.107.2', '10.0.107.3', '10.0.107.4',
    '10.0.107.51', '10.0.107.61', '10.0.107.62', '10.0.107.63', '10.0.107.7',
    '10.0.107.8', '10.0.107.9', '10.0.108.1', '10.0.108.10', '10.0.108.11',
    '10.0.108.12', '10.0.108.2', '10.0.108.3', '10.0.108.4', '10.0.108.5',
    '10.0.108.51', '10.0.108.52', '10.0.108.6', '10.0.108.7', '10.0.108.8',
    '10.0.108.9', '10.0.200.1', '10.0.200.2', '10.0.200.3', '10.0.200.4',
    '10.0.200.5', '10.0.200.6'
]

# ✅ قائمة السويتشات
switch_ips = [
    '10.0.0.1', '10.0.0.2', '10.0.0.3', '10.0.0.4', 
    '10.0.101.101','10.0.101.102', '10.0.101.103', '10.0.101.104', '10.0.101.105', 
    '10.0.102.101', '10.0.102.102', '10.0.102.103', '10.0.102.104', '10.0.103.101',
    '10.0.103.102', '10.0.103.103', '10.0.103.104', '10.0.103.105', '10.0.103.106',
    '10.0.103.107', '10.0.103.108', '10.0.104.101', '10.0.104.102', '10.0.104.103',
    '10.0.104.104', '10.0.105.101', '10.0.106.101', '10.0.106.102', '10.0.106.103',
    '10.0.106.104', '10.0.107.101', '10.0.107.102', '10.0.107.103', '10.0.107.104',
    '10.0.200.101'
]

# واجهة البرنامج
root = tk.Tk()
root.title("Camera & Switch Checker")
root.attributes("-fullscreen", True)
root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))
root.configure(bg="white")

btn = tk.Button(root, text="Network Scanning 🔍", command=lambda: check_ips(),
                font=("Arial", 12), bg="#007acc", fg="white", height=2)
btn.pack(pady=(10, 5), fill="x", padx=20)

status_label = tk.Label(root, text="", font=("Arial", 10), bg="white", fg="black")
status_label.pack(pady=(0, 5))

container = tk.Frame(root)
canvas = tk.Canvas(container, bg="white", highlightthickness=0)
scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg="white")

scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

def is_ip_up(ip, attempts=4):
    success = 0
    for _ in range(attempts):
        if ping(ip, timeout=1):
            success += 1
    return success >= 2

def open_ip_in_browser(event, ip_address):
    webbrowser.open(f"http://{ip_address}")

def draw_section(title, ip_list, start_row):
    row = start_row
    col = 0
    num_columns = 16

    # عنوان القسم في الوسط
    title_label = tk.Label(scrollable_frame, text=title, font=("Arial", 12, "bold"),
                           bg="lightgray")
    title_label.grid(row=row, column=0, columnspan=num_columns, sticky="nsew")
    title_label.configure(anchor="center")
    row += 1

    for ip in ip_list:
        result = is_ip_up(ip)
        status = "✅ UP" if result else "❌ DOWN"
        bg_color = "#d4edda" if result else "#f8d7da"
        fg_color = "#155724" if result else "#721c24"

        label = tk.Label(scrollable_frame, text=f"{ip}\n{status}",
                         font=("Arial", 10), bg=bg_color, fg=fg_color,
                         width=9, height=3, relief="solid", borderwidth=1)
        label.bind("<Double-Button-1>", lambda e, ip=ip: open_ip_in_browser(e, ip))
        label.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")

        col += 1
        if col >= num_columns:
            col = 0
            row += 1

    return row + 1  # next starting row

def check_ips():
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    status_label.config(text="جاري الفحص...")

    def ping_all():
        row = draw_section("Camera IPs 📷", camera_ips, 0)
        draw_section("Switch IPs 🖧", switch_ips, row)
        status_label.config(text="✅ تم الانتهاء من الفحص")

    Thread(target=ping_all).start()

root.mainloop()
import os
from tkinter import *
from tkinter import messagebox
import subprocess

# Danh sách server và đường dẫn start.bat
servers = {
    "CenterServer": r"D:\LTZS_BL20166.Com\server\bin\centerserver\start.bat",
    "DBServer": r"D:\LTZS_BL20166.Com\server\bin\dbserver\start.bat",
    "GameWorld": r"D:\LTZS_BL20166.Com\server\bin\gameworld\start.bat",
    "Gateway": r"D:\LTZS_BL20166.Com\server\bin\gateway\start.bat"
}

# Lưu tiến trình để sau có thể kill (giả lập dừng server)
processes = {}

# Hàm khởi động server
def start_server(name, path):
    if not os.path.exists(path):
        messagebox.showerror("Lỗi", f"Không tìm thấy file: {path}")
        return
    try:
        p = subprocess.Popen(["cmd.exe", "/c", "start", path], shell=True)
        processes[name] = p
        status_labels[name].config(text="🟢 Đang chạy")
    except Exception as e:
        messagebox.showerror("Lỗi", str(e))

# Hàm tắt server
def stop_server(name):
    os.system(f"taskkill /f /fi \"WINDOWTITLE eq {name}\"")
    status_labels[name].config(text="🔴 Đã tắt")

# Tạo giao diện
root = Tk()
root.title("Tool Chạy Server Lôi Đình H5 - THCGaming")
root.geometry("500x320")
root.configure(bg="#f4f4f8")

title = Label(root, text="Khởi Động Server Lôi Đình H5 - THCGaming", font=("Segoe UI", 14, "bold"), bg="#f4f4f8", fg="#2c3e50")
title.pack(pady=10)

frame = Frame(root, bg="#f4f4f8")
frame.pack(pady=10)

status_labels = {}

for i, (name, path) in enumerate(servers.items()):
    lbl = Label(frame, text=name, width=15, anchor="w", font=("Segoe UI", 11), bg="#f4f4f8")
    lbl.grid(row=i, column=0, padx=10, pady=5)

    btn_start = Button(frame, text="Khởi động", command=lambda n=name, p=path: start_server(n, p), bg="#27ae60", fg="white", width=10)
    btn_start.grid(row=i, column=1, padx=5)

    btn_stop = Button(frame, text="Tắt", command=lambda n=name: stop_server(n), bg="#c0392b", fg="white", width=6)
    btn_stop.grid(row=i, column=2, padx=5)

    status = Label(frame, text="🔴 Đã tắt", fg="gray", bg="#f4f4f8", font=("Segoe UI", 10))
    status.grid(row=i, column=3, padx=10)
    status_labels[name] = status

# Nút khởi động tất cả
def start_all():
    for name, path in servers.items():
        start_server(name, path)

def stop_all():
    for name in servers:
        stop_server(name)

bottom_frame = Frame(root, bg="#f4f4f8")
bottom_frame.pack(pady=15)

Button(bottom_frame, text="Khởi động tất cả", command=start_all, bg="#2980b9", fg="white", width=16).grid(row=0, column=0, padx=10)
Button(bottom_frame, text="Tắt tất cả", command=stop_all, bg="#8e44ad", fg="white", width=16).grid(row=0, column=1, padx=10)

root.mainloop()

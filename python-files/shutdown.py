import os
import platform
import subprocess
import tkinter as tk
from tkinter import messagebox

system_name = platform.system()

def shutdown_pc(delay_seconds=0):
    # Thông báo trước
    if delay_seconds == 0:
        messagebox.showinfo("Thông báo", "Máy sẽ tắt ngay.")
    else:
        messagebox.showinfo("Thông báo", f"Máy sẽ tắt sau {delay_seconds//60} phút.")

    # Gọi lệnh shutdown
    if system_name == "Windows":
        subprocess.Popen(["shutdown", "/s", "/t", str(delay_seconds)], shell=False)
    elif system_name in ["Linux", "Darwin"]:
        if delay_seconds == 0:
            subprocess.Popen(["shutdown", "now"])
        else:
            subprocess.Popen(["shutdown", f"+{delay_seconds//60}"])
    root.destroy()
    os._exit(0)

def restart_pc():
    messagebox.showinfo("Thông báo", "Máy sẽ khởi động lại ngay.")
    if system_name == "Windows":
        subprocess.Popen(["shutdown", "/r", "/t", "0"], shell=False)
    elif system_name in ["Linux", "Darwin"]:
        subprocess.Popen(["reboot"])
    root.destroy()
    os._exit(0)

def sleep_pc():
    messagebox.showinfo("Thông báo", "Máy sẽ chuyển sang chế độ Sleep.")
    if system_name == "Windows":
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    elif system_name == "Linux":
        os.system("systemctl suspend")
    elif system_name == "Darwin":
        os.system("pmset sleepnow")
    root.destroy()
    os._exit(0)

def cancel_timer():
    if system_name == "Windows":
        os.system("shutdown /a")
    messagebox.showinfo("Thông báo", "Đã hủy lịch hẹn.")

# === GUI ===
root = tk.Tk()
root.title("Quản lý Nguồn Máy Tính")
root.geometry("400x550")
root.resizable(False, False)

label = tk.Label(root, text="Chọn thao tác", font=("Arial", 14, "bold"))
label.pack(pady=10)

frame_shutdown = tk.LabelFrame(root, text="Tắt máy", font=("Arial", 12))
frame_shutdown.pack(pady=10, fill="x", padx=20)

tk.Button(frame_shutdown, text="Ngay lập tức", font=("Arial", 12),
          command=lambda: shutdown_pc(0)).pack(pady=2, fill="x")

for minutes in [5, 10, 15, 20, 30, 60]:
    tk.Button(frame_shutdown, text=f"Sau {minutes} phút", font=("Arial", 12),
              command=lambda m=minutes: shutdown_pc(m * 60)).pack(pady=2, fill="x")

tk.Button(root, text="Khởi động lại", font=("Arial", 12), bg="lightblue",
          command=restart_pc).pack(pady=10, fill="x", padx=20)

tk.Button(root, text="Sleep", font=("Arial", 12), bg="lightgreen",
          command=sleep_pc).pack(pady=10, fill="x", padx=20)

tk.Button(root, text="Hủy lịch hẹn", font=("Arial", 12), bg="orange",
          command=cancel_timer).pack(pady=10, fill="x", padx=20)

tk.Button(root, text="Thoát", font=("Arial", 12), bg="lightcoral",
          command=root.destroy).pack(pady=10, fill="x", padx=20)

root.mainloop()

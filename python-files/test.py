import os
import platform
import time
import threading
import tkinter as tk
from tkinter import messagebox
import json
import pathlib

# === Cấu hình file lưu tiến trình ===
TIMER_FILE = pathlib.Path("shutdown_timer.json")
system_name = platform.system()
countdown_job = None  # Lưu job đếm ngược của Tkinter

# === Hàm lưu tiến trình ===
def save_timer(mode, end_time):
    with open(TIMER_FILE, "w") as f:
        json.dump({"mode": mode, "end_time": end_time}, f)

# === Hàm tải tiến trình ===
def load_timer():
    if TIMER_FILE.exists():
        with open(TIMER_FILE, "r") as f:
            try:
                data = json.load(f)
                return data
            except:
                return None
    return None

# === Xóa tiến trình ===
def clear_timer():
    if TIMER_FILE.exists():
        TIMER_FILE.unlink()

# === Chạy lệnh hệ thống ===
def execute_command(command, delay=0):
    def run():
        if delay > 0:
            time.sleep(delay)
        os.system(command)
        clear_timer()
    threading.Thread(target=run, daemon=True).start()

def shutdown_pc(delay_seconds):
    if system_name == "Windows":
        execute_command(f"shutdown /s /t {delay_seconds}")
    elif system_name in ["Linux", "Darwin"]:
        execute_command("sudo shutdown now", delay_seconds)

def restart_pc():
    if system_name == "Windows":
        execute_command("shutdown /r /t 0")
    elif system_name in ["Linux", "Darwin"]:
        execute_command("sudo reboot")

def sleep_pc():
    try:
        if system_name == "Windows":
            result = os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            if result != 0:
                raise Exception("Không thể đưa máy vào chế độ Sleep.")
        elif system_name == "Linux":
            result = os.system("systemctl suspend")
            if result != 0:
                raise Exception("Không thể đưa máy vào chế độ Sleep.")
        elif system_name == "Darwin":
            result = os.system("pmset sleepnow")
            if result != 0:
                raise Exception("Không thể đưa máy vào chế độ Sleep.")
    except Exception as e:
        messagebox.showerror("Lỗi", str(e))

# === Hủy lệnh hẹn giờ ===
def cancel_timer():
    global countdown_job
    confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc muốn hủy lịch hẹn?")
    if confirm:
        if system_name == "Windows":
            os.system("shutdown /a")
        clear_timer()
        countdown_label.config(text="")
        if countdown_job:
            root.after_cancel(countdown_job)
            countdown_job = None
        messagebox.showinfo("Thông báo", "Đã hủy lịch hẹn.")

# === Đếm ngược thời gian ===
def update_countdown(end_time):
    global countdown_job
    remaining = int(end_time - time.time())
    if remaining > 0:
        minutes = remaining // 60
        seconds = remaining % 60
        countdown_label.config(text=f"Còn lại: {minutes:02d}:{seconds:02d}")
        countdown_job = root.after(1000, update_countdown, end_time)
    else:
        countdown_label.config(text="")
        clear_timer()

# === Đặt hẹn tắt máy ===
def confirm_shutdown(minutes):
    data = load_timer()
    now = time.time()
    new_end = now + minutes * 60

    if data:
        remaining = int(data["end_time"] - now)
        if remaining > 0:
            remaining_min = remaining // 60
            if minutes < remaining_min:
                messagebox.showwarning("Cảnh báo",
                                       f"Bạn đã hẹn {remaining_min} phút, không thể giảm xuống {minutes} phút.")
                return
            else:
                messagebox.showinfo("Thông báo", f"Đã tăng thời gian từ {remaining_min} phút lên {minutes} phút.")
        save_timer("shutdown", new_end)
    else:
        confirm = messagebox.askyesno("Xác nhận", f"Tắt máy sau {minutes} phút?")
        if not confirm:
            return
        save_timer("shutdown", new_end)
        messagebox.showinfo("Thông báo", f"Máy sẽ tắt sau {minutes} phút.")

    shutdown_pc(minutes * 60)
    update_countdown(new_end)

def confirm_shutdown_now():
    confirm = messagebox.askyesno("Xác nhận", "Tắt máy ngay?")
    if confirm:
        save_timer("shutdown", time.time())
        messagebox.showinfo("Thông báo", "Máy sẽ tắt ngay bây giờ.")
        shutdown_pc(0)

def confirm_restart():
    confirm = messagebox.askyesno("Xác nhận", "Khởi động lại ngay?")
    if confirm:
        save_timer("restart", time.time())
        messagebox.showinfo("Thông báo", "Máy sẽ khởi động lại ngay bây giờ.")
        restart_pc()

def confirm_sleep():
    confirm = messagebox.askyesno("Xác nhận", "Đưa vào chế độ Sleep?")
    if confirm:
        messagebox.showinfo("Thông báo", "Máy sẽ chuyển sang chế độ Sleep.")
        sleep_pc()

# === Khôi phục tiến trình khi mở lại ===
def restore_timer_info():
    data = load_timer()
    if data:
        remaining = int(data["end_time"] - time.time())
        if remaining > 0:
            minutes = remaining // 60
            seconds = remaining % 60
            messagebox.showinfo("Tiến trình",
                                f"Đang hẹn {data['mode']} sau {minutes} phút {seconds} giây.")
            update_countdown(data["end_time"])
        else:
            clear_timer()

# === GUI ===
root = tk.Tk()
root.title("Quản lý Nguồn Máy Tính")
root.geometry("400x550")
root.resizable(False, False)

label = tk.Label(root, text="Chọn thao tác", font=("Arial", 14, "bold"))
label.pack(pady=10)

countdown_label = tk.Label(root, text="", font=("Arial", 14), fg="red")
countdown_label.pack(pady=5)

frame_shutdown = tk.LabelFrame(root, text="Tắt máy", font=("Arial", 12))
frame_shutdown.pack(pady=10, fill="x", padx=20)

tk.Button(frame_shutdown, text="Ngay lập tức", font=("Arial", 12),
          command=confirm_shutdown_now).pack(pady=2, fill="x")

for minutes in [5, 10, 15, 20, 30, 60]:
    tk.Button(frame_shutdown, text=f"Sau {minutes} phút", font=("Arial", 12),
              command=lambda m=minutes: confirm_shutdown(m)).pack(pady=2, fill="x")

tk.Button(root, text="Khởi động lại", font=("Arial", 12), bg="lightblue",
          command=confirm_restart).pack(pady=10, fill="x", padx=20)

tk.Button(root, text="Sleep", font=("Arial", 12), bg="lightgreen",
          command=confirm_sleep).pack(pady=10, fill="x", padx=20)

tk.Button(root, text="Hủy lịch hẹn", font=("Arial", 12), bg="orange",
          command=cancel_timer).pack(pady=10, fill="x", padx=20)

tk.Button(root, text="Thoát", font=("Arial", 12), bg="lightcoral",
          command=root.destroy).pack(pady=10, fill="x", padx=20)

restore_timer_info()

root.mainloop()

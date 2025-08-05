# -*- coding: utf-8 -*-
"""
Ứng dụng hẹn giờ tắt máy tính cho Windows.
Chương trình sử dụng thư viện tkinter để tạo giao diện người dùng và thư viện os để thực thi lệnh tắt máy.
"""

import tkinter as tk
from tkinter import messagebox
import os
def set_shutdown_timer():
    """Thiết lập hẹn giờ tắt máy tính."""
    try:
        # Lấy số phút từ ô nhập liệu
        minutes = int(entry_minutes.get())
        if minutes <= 0:
            messagebox.showerror("Lỗi", "Vui lòng nhập một số phút lớn hơn 0.")
            return

        # Chuyển đổi phút sang giây
        seconds = minutes * 60

        # Lệnh tắt máy tính trên Windows: shutdown /s /t <số giây>
        # /s: Tắt máy
        # /t: Đặt thời gian chờ trước khi tắt
        command = f'shutdown /s /t {seconds}'

        # Thực thi lệnh
        os.system(command)
        
        messagebox.showinfo("Thành công", f"Máy tính sẽ tắt sau {minutes} phút.")
        root.destroy() # Đóng ứng dụng sau khi thiết lập thành công

    except ValueError:
        messagebox.showerror("Lỗi", "Vui lòng nhập một số nguyên hợp lệ.")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {e}")

def cancel_shutdown_timer():
    """Hủy bỏ hẹn giờ tắt máy đã thiết lập."""
    # Lệnh hủy hẹn giờ tắt máy trên Windows: shutdown /a
    # /a: Hủy bỏ lệnh tắt máy hệ thống
    command = 'shutdown /a'

    # Thực thi lệnh
    os.system(command)
    
    messagebox.showinfo("Thông báo", "Hẹn giờ tắt máy đã được hủy bỏ.")
    root.destroy() # Đóng ứng dụng sau khi hủy bỏ

# --- Tạo giao diện người dùng ---

# Tạo cửa sổ chính
root = tk.Tk()
root.title("Hẹn giờ Tắt Máy")
root.geometry("350x180")
root.resizable(False, False)

# Tiêu đề
label_title = tk.Label(root, text="Hẹn giờ Tắt Máy Tính", font=("Helvetica", 16, "bold"))
label_title.pack(pady=10)

# Khung chứa các thành phần nhập liệu
frame_input = tk.Frame(root)
frame_input.pack(pady=5)

# Nhãn hướng dẫn
label_minutes = tk.Label(frame_input, text="Nhập số phút:", font=("Helvetica", 12))
label_minutes.pack(side=tk.LEFT)

# Ô nhập liệu
entry_minutes = tk.Entry(frame_input, font=("Helvetica", 12), width=10)
entry_minutes.pack(side=tk.LEFT, padx=5)
entry_minutes.focus_set() # Tự động đặt con trỏ vào ô nhập liệu

# Khung chứa các nút bấm
frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=10)

# Nút "Hẹn giờ"
btn_set = tk.Button(frame_buttons, text="Hẹn giờ", command=set_shutdown_timer, bg="#4CAF50", fg="white", font=("Helvetica", 12))
btn_set.pack(side=tk.LEFT, padx=10)

# Nút "Hủy hẹn giờ"
btn_cancel = tk.Button(frame_buttons, text="Hủy hẹn giờ", command=cancel_shutdown_timer, bg="#F44336", fg="white", font=("Helvetica", 12))
btn_cancel.pack(side=tk.LEFT, padx=10)

# Bắt đầu vòng lặp sự kiện của cửa sổ
root.mainloop()



import os
import tkinter as tk
from tkinter import messagebox

def schedule_shutdown():
    try:
        minutes = int(entry.get())
        if minutes <= 0:
            raise ValueError
        seconds = minutes * 60
        os.system(f"shutdown /s /t {seconds}")
        messagebox.showinfo("예약 완료", f"{minutes}분 후 컴퓨터가 종료됩니다.")
    except ValueError:
        messagebox.showerror("입력 오류", "1 이상의 숫자(분)를 입력해주세요.")

def cancel_shutdown():
    os.system("shutdown /a")
    messagebox.showinfo("예약 취소", "종료 예약이 취소되었습니다.")

# GUI 생성
root = tk.Tk()
root.title("컴퓨터 자동 종료 프로그램")
root.geometry("350x200")
root.resizable(False, False)

tk.Label(root, text="종료까지 시간 (분)", font=("Arial", 14)).pack(pady=10)

entry = tk.Entry(root, font=("Arial", 14), justify="center")
entry.insert(0, "10")
entry.pack()

button_frame = tk.Frame(root)
button_frame.pack(pady=20)

tk.Button(button_frame, text="종료 예약", font=("Arial", 12), width=12, command=schedule_shutdown).grid(row=0, column=0, padx=10)
tk.Button(button_frame, text="예약 취소", font=("Arial", 12), width=12, command=cancel_shutdown).grid(row=0, column=1, padx=10)

root.mainloop()

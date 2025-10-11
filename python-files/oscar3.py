#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 11 23:11:38 2025

@author: jessica
"""

import tkinter as tk
from tkinter import messagebox

def calculate():
    try:
        x = float(entry_x.get())
        t = (430 - x) / 2
        c = t + 5
        label_result.config(text=f"T = {t:.2f}\nC = {c:.2f}")
        root.clipboard_clear()
        root.clipboard_append(f"T = {t:.2f}, C = {c:.2f}")
    except ValueError:
        messagebox.showerror("錯誤", "請輸入有效的數字！")

# 驗證輸入，只允許數字和小數點
def validate_input(new_value):
    if new_value == "":
        return True
    try:
        float(new_value)
        return True
    except ValueError:
        return False

# GUI 設定
root = tk.Tk()
root.title("T、C 計算小工具")
root.geometry("300x200")
root.configure(bg="#e8f0fe")

title_label = tk.Label(root, text="T / C 計算器", font=("Segoe UI", 14, "bold"), bg="#e8f0fe", fg="#1a73e8")
title_label.pack(pady=10)

frame = tk.Frame(root, bg="#e8f0fe")
frame.pack()

tk.Label(frame, text="輸入 X 值：", bg="#e8f0fe", font=("Segoe UI", 11)).grid(row=0, column=0, padx=5, pady=5)

# 設定 Entry 驗證
vcmd = (root.register(validate_input), "%P")
entry_x = tk.Entry(frame, width=15, font=("Segoe UI", 11), validate="key", validatecommand=vcmd)
entry_x.grid(row=0, column=1, padx=5, pady=5)

calc_button = tk.Button(root, text="計算", command=calculate, bg="#1a73e8", fg="white", font=("Segoe UI", 11), width=12, relief="flat")
calc_button.pack(pady=10)

label_result = tk.Label(root, text="T = \nC = ", bg="#e8f0fe", font=("Segoe UI", 12))
label_result.pack(pady=5)

# 按下 Enter 鍵也能計算
root.bind('<Return>', lambda event: calculate())

root.mainloop()

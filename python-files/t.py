import tkinter as tk
from tkinter import simpledialog, messagebox

def main():
    # 建立隱藏主視窗
    root = tk.Tk()
    root.withdraw()  # 隱藏主視窗

    while True:
        try:
            # 彈出輸入框要求 X
            x_input = simpledialog.askstring("T 計算器", "請輸入 X 值（數字）：")
            if x_input is None:
                # 使用者按取消
                break

            x = float(x_input.strip())
            t = (430 - x) / 2

            # 自動複製到剪貼簿
            root.clipboard_clear()
            root.clipboard_append(f"T = {t:.2f}")

            # 顯示結果提示
            messagebox.showinfo("計算結果", f"T = {t:.2f} 已複製到剪貼簿")
            break  # 計算一次就結束程式
        except ValueError:
            messagebox.showerror("錯誤", "請輸入有效的數字！")

    root.destroy()

if __name__ == "__main__":
    main()

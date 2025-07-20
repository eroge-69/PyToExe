import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading
import keyboard

API_URL = "https://atd.hpsuzuki.net/api-json.php?keyword="

class SearchPartsApp:
    def __init__(self):
        self.root = None

    def create_window(self):
        if self.root and tk.Toplevel.winfo_exists(self.root):
            return  # Nếu đang mở thì không tạo mới

        self.root = tk.Tk()
        self.root.title("Tìm kiếm phụ tùng")
        self.root.geometry("900x500")
        self.root.resizable(False, False)

        # Đóng bằng ESC
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        tk.Label(self.root, text="Nhập mã phụ tùng:").pack(pady=5)
        self.entry = tk.Entry(self.root, font=("Arial", 14))
        self.entry.pack(pady=5, fill=tk.X, padx=20)
        self.entry.bind("<Return>", lambda e: self.search())

        self.tree = ttk.Treeview(self.root, columns=("ma","ten","gia_szk","gia_hhp","loai_xe","ma_cu","xuat_xu","hd"), show="headings")
        headings = ["MÃ PHỤ TÙNG","TÊN PHỤ TÙNG","GIÁ SZK","GIÁ HHP","LOẠI XE","MÃ CŨ","XUẤT XỨ","HĐ"]
        for i, h in enumerate(headings):
            self.tree.heading(i, text=h)
            self.tree.column(i, width=100, anchor="center")
        self.tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.root.mainloop()

    def search(self):
        keyword = self.entry.get().strip()
        if not keyword:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập mã phụ tùng")
            return

        threading.Thread(target=self.fetch_data, args=(keyword,), daemon=True).start()

    def fetch_data(self, keyword):
        try:
            res = requests.get(API_URL + keyword)
            data = res.json()
            self.update_table(data)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lấy dữ liệu: {e}")

    def update_table(self, data):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for item in data:
            self.tree.insert("", tk.END, values=(
                item.get("ma",""),
                item.get("ten",""),
                item.get("gia_szk",""),
                item.get("gia_hhp",""),
                item.get("loai_xe",""),
                item.get("ma_cu",""),
                item.get("xuat_xu",""),
                item.get("hd_link","")
            ))

app = SearchPartsApp()

def hotkey_listener():
    while True:
        keyboard.wait("alt+x")
        app.create_window()

threading.Thread(target=hotkey_listener, daemon=True).start()

# Giữ chương trình chạy ngầm
keyboard.wait("esc")

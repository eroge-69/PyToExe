import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class RenameTool:
    def __init__(self, master):
        self.master = master
        master.title("ĐỔI TÊN FILE HÀNG LOẠT")

        self.directory = tk.StringVar()
        self.prefix = tk.StringVar()
        self.suffix = tk.StringVar()
        self.find_text = tk.StringVar()
        self.replace_text = tk.StringVar()
        self.start_number = tk.IntVar(value=1)
        self.use_numbering = tk.BooleanVar()
        self.uppercase = tk.BooleanVar()
        self.lowercase = tk.BooleanVar()

        self.create_widgets()

    def create_widgets(self):
        tk.Label(root, text="Chọn thư mục:").grid(row=0, column=0, sticky="w")
        tk.Entry(root, textvariable=self.directory, width=50).grid(row=0, column=1)
        tk.Button(root, text="Duyệt", command=self.browse_folder).grid(row=0, column=2)

        tk.Checkbutton(root, text="Đánh số tự động (0001...)", variable=self.use_numbering).grid(row=1, column=0, sticky="w")
        tk.Label(root, text="Bắt đầu từ số:").grid(row=1, column=1, sticky="e")
        tk.Entry(root, textvariable=self.start_number, width=5).grid(row=1, column=2, sticky="w")

        tk.Label(root, text="Thêm tiền tố:").grid(row=2, column=0, sticky="w")
        tk.Entry(root, textvariable=self.prefix).grid(row=2, column=1)

        tk.Label(root, text="Thêm hậu tố:").grid(row=3, column=0, sticky="w")
        tk.Entry(root, textvariable=self.suffix).grid(row=3, column=1)

        tk.Label(root, text="Tìm:").grid(row=4, column=0, sticky="w")
        tk.Entry(root, textvariable=self.find_text).grid(row=4, column=1)

        tk.Label(root, text="Thay bằng:").grid(row=5, column=0, sticky="w")
        tk.Entry(root, textvariable=self.replace_text).grid(row=5, column=1)

        tk.Checkbutton(root, text="Viết HOA", variable=self.uppercase).grid(row=6, column=0, sticky="w")
        tk.Checkbutton(root, text="viết thường", variable=self.lowercase).grid(row=6, column=1, sticky="w")

        tk.Button(root, text="ĐỔI TÊN", bg="green", fg="white", command=self.rename_files).grid(row=7, column=1, pady=10)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.directory.set(folder)

    def rename_files(self):
        folder = self.directory.get()
        if not os.path.isdir(folder):
            messagebox.showerror("Lỗi", "Thư mục không hợp lệ.")
            return

        files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        num = self.start_number.get()

        for fname in files:
            name, ext = os.path.splitext(fname)
            new_name = name

            if self.find_text.get():
                new_name = new_name.replace(self.find_text.get(), self.replace_text.get())

            if self.uppercase.get():
                new_name = new_name.upper()
            elif self.lowercase.get():
                new_name = new_name.lower()

            new_name = self.prefix.get() + new_name + self.suffix.get()

            if self.use_numbering.get():
                new_name = f"{str(num).zfill(4)}_{new_name}"
                num += 1

            new_path = os.path.join(folder, new_name + ext)
            old_path = os.path.join(folder, fname)

            try:
                os.rename(old_path, new_path)
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể đổi tên {fname}:
{e}")

        messagebox.showinfo("Xong", "Đã đổi tên tất cả file.")

root = tk.Tk()
app = RenameTool(root)
root.mainloop()

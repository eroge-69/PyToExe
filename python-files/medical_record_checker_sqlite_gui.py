import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import sqlite3
import threading
DB_NAME = ":memory:"  # dùng RAM, muốn lưu file thì đổi tên file db

def load_to_db(df, conn):
    # Chuẩn hoá định dạng thời gian cho SQLite
    for col in ["Thời gian bắt đầu thực hiện", "Thời gian có kết quả"]:
        df[col] = pd.to_datetime(df[col]).dt.strftime("%Y-%m-%d %H:%M:%S")
    df.to_sql("records", conn, index=False, if_exists="replace")

def query_errors(conn):
    # Lỗi 1: 1 mã hồ sơ dùng 2 dịch vụ khác nhau cùng thời gian
    query1 = """
    SELECT a."Mã hồ sơ", a."tên dịch vụ" as dv1, b."tên dịch vụ" as dv2,
           a."Thời gian bắt đầu thực hiện" as start1, a."Thời gian có kết quả" as end1,
           b."Thời gian bắt đầu thực hiện" as start2, b."Thời gian có kết quả" as end2
    FROM records a
    JOIN records b ON a."Mã hồ sơ" = b."Mã hồ sơ" AND a."tên dịch vụ" != b."tên dịch vụ"
    WHERE
        (datetime(a."Thời gian bắt đầu thực hiện") <= datetime(b."Thời gian có kết quả") AND
         datetime(b."Thời gian bắt đầu thực hiện") <= datetime(a."Thời gian có kết quả"))
    AND a.rowid < b.rowid
    """
    # Lỗi 2: Người thực hiện chính/phụ làm 2 hồ sơ khác nhau cùng lúc
    query2 = """
    SELECT a."Người thực hiện chính" as nguoi, a."Mã hồ sơ" as hs1, b."Mã hồ sơ" as hs2,
           a."tên dịch vụ" as dv1, b."tên dịch vụ" as dv2,
           a."Thời gian bắt đầu thực hiện" as start1, a."Thời gian có kết quả" as end1,
           b."Thời gian bắt đầu thực hiện" as start2, b."Thời gian có kết quả" as end2
    FROM records a
    JOIN records b ON a."Người thực hiện chính" = b."Người thực hiện chính"
                  AND a."Mã hồ sơ" != b."Mã hồ sơ"
    WHERE a."Người thực hiện chính" IS NOT NULL AND a."Người thực hiện chính" != ''
      AND (datetime(a."Thời gian bắt đầu thực hiện") <= datetime(b."Thời gian có kết quả")
           AND datetime(b."Thời gian bắt đầu thực hiện") <= datetime(a."Thời gian có kết quả"))
    AND a.rowid < b.rowid
    """
    query3 = """
    SELECT a."Người thực hiện phụ" as nguoi, a."Mã hồ sơ" as hs1, b."Mã hồ sơ" as hs2,
           a."tên dịch vụ" as dv1, b."tên dịch vụ" as dv2,
           a."Thời gian bắt đầu thực hiện" as start1, a."Thời gian có kết quả" as end1,
           b."Thời gian bắt đầu thực hiện" as start2, b."Thời gian có kết quả" as end2
    FROM records a
    JOIN records b ON a."Người thực hiện phụ" = b."Người thực hiện phụ"
                  AND a."Mã hồ sơ" != b."Mã hồ sơ"
    WHERE a."Người thực hiện phụ" IS NOT NULL AND a."Người thực hiện phụ" != ''
      AND (datetime(a."Thời gian bắt đầu thực hiện") <= datetime(b."Thời gian có kết quả")
           AND datetime(b."Thời gian bắt đầu thực hiện") <= datetime(a."Thời gian có kết quả"))
    AND a.rowid < b.rowid
    """

    df1 = pd.read_sql(query1, conn)
    df1["Loại lỗi"] = "1 mã hồ sơ dùng 2 dịch vụ khác nhau cùng thời gian"
    df1["Người thực hiện"] = ""
    df1["Mã hồ sơ 1"] = ""
    df1["Mã hồ sơ 2"] = ""

    df2 = pd.read_sql(query2, conn)
    df2["Loại lỗi"] = "Người thực hiện chính làm 2 mã hồ sơ khác nhau cùng thời gian"
    df2.rename(columns={"nguoi": "Người thực hiện"}, inplace=True)
    df2["Mã hồ sơ"] = ""
    df2["Dịch vụ 1"] = df2["dv1"]
    df2["Dịch vụ 2"] = df2["dv2"]
    df2["Mã hồ sơ 1"] = df2["hs1"]
    df2["Mã hồ sơ 2"] = df2["hs2"]

    df3 = pd.read_sql(query3, conn)
    df3["Loại lỗi"] = "Người thực hiện phụ làm 2 mã hồ sơ khác nhau cùng thời gian"
    df3.rename(columns={"nguoi": "Người thực hiện"}, inplace=True)
    df3["Mã hồ sơ"] = ""
    df3["Dịch vụ 1"] = df3["dv1"]
    df3["Dịch vụ 2"] = df3["dv2"]
    df3["Mã hồ sơ 1"] = df3["hs1"]
    df3["Mã hồ sơ 2"] = df3["hs2"]

    # Chuẩn hóa thứ tự cột xuất ra
    columns = [
        "Loại lỗi", "Mã hồ sơ", "Dịch vụ 1", "Dịch vụ 2",
        "Người thực hiện", "Mã hồ sơ 1", "Mã hồ sơ 2",
        "start1", "end1", "start2", "end2"
    ]

    df1["Dịch vụ 1"] = df1["dv1"]
    df1["Dịch vụ 2"] = df1["dv2"]

    df1 = df1.rename(columns={"start1": "Thời gian 1", "end1": "KQ 1", "start2": "Thời gian 2", "end2": "KQ 2"})
    df2 = df2.rename(columns={"start1": "Thời gian 1", "end1": "KQ 1", "start2": "Thời gian 2", "end2": "KQ 2"})
    df3 = df3.rename(columns={"start1": "Thời gian 1", "end1": "KQ 1", "start2": "Thời gian 2", "end2": "KQ 2"})

    df1 = df1[
        ["Loại lỗi", "Mã hồ sơ", "Dịch vụ 1", "Dịch vụ 2", "Người thực hiện", "Mã hồ sơ 1", "Mã hồ sơ 2", "Thời gian 1", "KQ 1", "Thời gian 2", "KQ 2"]
    ]
    df2 = df2[
        ["Loại lỗi", "Mã hồ sơ", "Dịch vụ 1", "Dịch vụ 2", "Người thực hiện", "Mã hồ sơ 1", "Mã hồ sơ 2", "Thời gian 1", "KQ 1", "Thời gian 2", "KQ 2"]
    ]
    df3 = df3[
        ["Loại lỗi", "Mã hồ sơ", "Dịch vụ 1", "Dịch vụ 2", "Người thực hiện", "Mã hồ sơ 1", "Mã hồ sơ 2", "Thời gian 1", "KQ 1", "Thời gian 2", "KQ 2"]
    ]

    return pd.concat([df1, df2, df3], ignore_index=True)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Dungpt- Kiểm tra trùng dịch vụ CLS- Thủ thuật -Ver1-")
        self.file_path = ""
        self.df = None
        self.conn = None
        self.errors = pd.DataFrame()

        frm_top = tk.Frame(root)
        frm_top.pack(padx=10, pady=10, fill="x")

        self.txt_file = tk.Entry(frm_top, width=60, state="readonly")
        self.txt_file.pack(side="left", padx=(0, 5))

        btn_browse = tk.Button(frm_top, text="Chọn file Excel", command=self.browse_file)
        btn_browse.pack(side="left")

        btn_check = tk.Button(frm_top, text="Kiểm tra", command=self.run_check_thread)
        btn_check.pack(side="left", padx=(5, 0))

        btn_export = tk.Button(frm_top, text="Xuất lỗi ra Excel", command=self.export_errors)
        btn_export.pack(side="left", padx=(5, 0))

        self.status = tk.Label(root, text="", fg="blue")
        self.status.pack(padx=10, anchor="w")

        columns = [
            "Loại lỗi", "Mã hồ sơ", "Dịch vụ 1", "Dịch vụ 2",
            "Người thực hiện", "Mã hồ sơ 1", "Mã hồ sơ 2",
            "Thời gian 1", "KQ 1", "Thời gian 2", "KQ 2"
        ]
        self.tree = ttk.Treeview(root, columns=columns, show="headings", height=16)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        self.tree.pack(padx=10, pady=(0,10), fill="both", expand=True)

    def browse_file(self):
        path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if path:
            self.file_path = path
            self.txt_file.config(state="normal")
            self.txt_file.delete(0, tk.END)
            self.txt_file.insert(0, path)
            self.txt_file.config(state="readonly")
            self.df = None
            self.errors = pd.DataFrame()
            self.status.config(text="")
            self.tree.delete(*self.tree.get_children())

    def run_check_thread(self):
        if not self.file_path:
            messagebox.showwarning("Chưa chọn file", "Vui lòng chọn file Excel.")
            return
        self.status.config(text="Đang kiểm tra...", fg="red")
        self.tree.delete(*self.tree.get_children())
        threading.Thread(target=self.run_check, daemon=True).start()

    def run_check(self):
        try:
            self.df = pd.read_excel(self.file_path)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Lỗi đọc file", str(e)))
            return
        self.conn = sqlite3.connect(DB_NAME)
        try:
            load_to_db(self.df, self.conn)
            errors = query_errors(self.conn)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Lỗi kiểm tra", str(e)))
            return
        self.errors = errors
        self.root.after(0, self.display_results)

    def display_results(self):
        self.tree.delete(*self.tree.get_children())
        if self.errors.empty:
            self.status.config(text="Không phát hiện lỗi trùng theo tiêu chí.", fg="blue")
        else:
            self.status.config(text=f"Tìm thấy {len(self.errors)} lỗi trùng.", fg="red")
            for _, row in self.errors.iterrows():
                self.tree.insert("", "end", values=list(row))

    def export_errors(self):
        if self.errors is None or self.errors.empty:
            messagebox.showinfo("Thông báo", "Không có lỗi để xuất.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if path:
            self.errors.to_excel(path, index=False)
            messagebox.showinfo("Thành công", f"Đã xuất file lỗi: {path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
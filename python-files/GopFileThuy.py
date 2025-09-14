import pandas as pd
from tkinter import Tk, filedialog
import os

def merge_excel_files():
    # Ẩn cửa sổ Tkinter gốc
    root = Tk()
    root.withdraw()

    # Chọn nhiều file Excel
    file_paths = filedialog.askopenfilenames(
        title="Chọn các file Excel cần gộp",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )

    if not file_paths:
        print("Bạn chưa chọn file nào.")
        return

    all_data = []

    # Đọc từng file
    for file in file_paths:
        try:
            # Đọc dữ liệu từ dòng 7 trở đi (tiêu đề ở dòng 6)
            df = pd.read_excel(file, header=5)  
            df["Tên_file_gốc"] = os.path.basename(file)  # Thêm cột nguồn gốc file
            all_data.append(df)
        except Exception as e:
            print(f"Lỗi khi đọc file {file}: {e}")

    if not all_data:
        print("Không có dữ liệu để gộp.")
        return

    # Gộp các DataFrame
    merged_df = pd.concat(all_data, ignore_index=True)

    # Chọn nơi lưu file kết quả
    save_path = filedialog.asksaveasfilename(
        title="Lưu file gộp",
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx")]
    )

    if save_path:
        # Xuất dữ liệu ra Excel
        merged_df.to_excel(save_path, index=False)
        print(f"Đã lưu file gộp tại: {save_path}")
    else:
        print("Bạn chưa chọn nơi lưu file.")

if __name__ == "__main__":
    merge_excel_files()


import zipfile
import os
import shutil
from tkinter import Tk, filedialog, messagebox

def extract_embedded_pdfs_from_xlsx(xlsx_path):
    base_folder = os.path.dirname(xlsx_path)
    temp_dir = os.path.join(base_folder, "temp_unzip")

    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)

    # Giải nén file .xlsx
    with zipfile.ZipFile(xlsx_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    embed_dir = os.path.join(temp_dir, 'xl', 'embeddings')
    if not os.path.exists(embed_dir):
        messagebox.showerror("Lỗi", f"Không tìm thấy file nhúng trong:\n{os.path.basename(xlsx_path)}")
        shutil.rmtree(temp_dir)
        return

    # Đổi tên và copy các file nhúng
    extracted = 0
    for i, fname in enumerate(os.listdir(embed_dir), 1):
        if fname.endswith('.bin'):
            source_path = os.path.join(embed_dir, fname)
            dest_path = os.path.join(base_folder, f"Embedded_{i}.pdf")
            shutil.copyfile(source_path, dest_path)
            extracted += 1

    shutil.rmtree(temp_dir)
    messagebox.showinfo("Hoàn tất", f"✅ Đã trích xuất {extracted} file PDF vào:\n{base_folder}")

def main():
    Tk().withdraw()  # Ẩn cửa sổ chính
    file_path = filedialog.askopenfilename(
        title="Chọn file Excel chứa PDF nhúng",
        filetypes=[("Excel files", "*.xlsx")]
    )

    if not file_path:
        return  # Người dùng hủy

    extract_embedded_pdfs_from_xlsx(file_path)

if __name__ == "__main__":
    main()

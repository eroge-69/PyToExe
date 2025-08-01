import os
import subprocess
import sys

# Đường dẫn thư mục input/output cùng cấp với script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
SOFFICE_PATH = r"C:\Program Files\LibreOffice\program\soffice.exe"

# Mapping định dạng file → filter
EXT_FILTERS = {
    ".doc": "pdf:writer_pdf_Export",
    ".docx": "pdf:writer_pdf_Export",
    ".xls": "pdf:calc_pdf_Export",
    ".xlsx": "pdf:calc_pdf_Export",
    ".ppt": "pdf:impress_pdf_Export",
    ".pptx": "pdf:impress_pdf_Export",
}

# Tạo thư mục input/output nếu chưa có
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"📥 Đọc từ: {INPUT_DIR}")
print(f"📤 Xuất ra: {OUTPUT_DIR}\n")

# Duyệt đệ quy input/
for root, _, files in os.walk(INPUT_DIR):
    for filename in files:
        name, ext = os.path.splitext(filename)
        ext = ext.lower()

        if ext not in EXT_FILTERS:
            print(f"⏩ Bỏ qua: {filename}")
            continue

        # Đường đầy đủ đến file input
        full_input_path = os.path.join(root, filename)

        # Tạo đường dẫn tương ứng trong output
        rel_path = os.path.relpath(root, INPUT_DIR)
        target_dir = os.path.join(OUTPUT_DIR, rel_path)
        os.makedirs(target_dir, exist_ok=True)

        output_pdf_path = os.path.join(target_dir, name + ".pdf")

        if os.path.exists(output_pdf_path):
            print(f"✅ Đã có: {output_pdf_path} → Bỏ qua")
            continue

        filter_str = EXT_FILTERS[ext]
        print(f"🔄 Đang chuyển: {filename} → {filter_str}")

        try:
            subprocess.run([
                SOFFICE_PATH,
                "--headless",
                "--convert-to", filter_str,
                full_input_path,
                "--outdir", target_dir
            ], check=True)
            print(f"✅ Đã tạo: {output_pdf_path}\n")
        except subprocess.CalledProcessError as e:
            print(f"❌ Lỗi khi chuyển {filename}: {e}")

# Mở thư mục output sau khi hoàn tất
print("\n🎉 Tất cả đã xong! Đang mở thư mục output...")
if sys.platform == "win32":
    os.startfile(OUTPUT_DIR)
elif sys.platform == "darwin":
    subprocess.run(["open", OUTPUT_DIR])
else:
    subprocess.run(["xdg-open", OUTPUT_DIR])

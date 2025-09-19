import re
import tkinter as tk
from tkinter import filedialog, messagebox
import os

# Gom nhóm các loại dấu
COMMA_CHARS = "[,，、]"         # dấu phẩy: Latin, Trung, Nhật, Hàn
PERIOD_CHARS = "[.。．]"        # dấu chấm: Latin, Trung, Nhật, Hàn
QUESTION_EXCLAM_CHARS = "[!?！？]"  # dấu hỏi/than: Latin + Đông Á

def remove_special(text: str) -> str:
    """Xoá ký tự đặc biệt và chuẩn hoá khoảng trắng."""
    brackets_pattern = r"[\"\'“”‘’\(\)\[\]\{\}（）【】「」『』《》〈〉〔〕]"
    cleaned = re.sub(brackets_pattern, "", text)
    cleaned = re.sub(r"\.{3,}|…", "", cleaned)  # xoá dấu ba chấm
    for sp in ["\u200b", "\u3000", "\u00A0", "\u202F", "\uFEFF"]:
        cleaned = cleaned.replace(sp, "")
    cleaned = re.sub(r"[ \t]+", " ", cleaned)  # gộp nhiều space/tab
    cleaned = "\n".join(line.strip() for line in cleaned.splitlines())
    return cleaned.lstrip()


def clean_mode_1(text: str) -> str:
    """Chế độ 1: Gộp đoạn (xoá xuống dòng, chuẩn hoá space)."""
    cleaned = remove_special(text)
    cleaned = cleaned.replace("\n", " ")
    cleaned = re.sub(r"[ ]+", " ", cleaned)  # chuẩn hoá nhiều space thành 1
    return cleaned.strip()


def clean_mode_2(text: str,
                 split_comma: bool = False,
                 split_period: bool = True,
                 split_qe: bool = True) -> str:
    """Chế độ 2: Chuẩn hoá sub (mọi ngôn ngữ)."""
    cleaned = remove_special(text)

    # Xuống dòng theo dấu chấm
    if split_period:
        cleaned = re.sub(f"({PERIOD_CHARS})", r"\1\n", cleaned)

    # Xuống dòng theo dấu phẩy
    if split_comma:
        cleaned = re.sub(f"({COMMA_CHARS})", r"\1\n", cleaned)

    # Xuống dòng theo ? !
    if split_qe:
        cleaned = re.sub(f"({QUESTION_EXCLAM_CHARS})", r"\1\n", cleaned)

    # Chuẩn hoá nhiều xuống dòng thành đúng 2
    cleaned = re.sub(r"\n+", "\n\n", cleaned)

    # Chuẩn hoá nhiều space trong dòng
    cleaned = re.sub(r"[ ]+", " ", cleaned)

    return cleaned.strip()


def process_files():
    file_paths = filedialog.askopenfilenames(
        title="Chọn file TXT",
        filetypes=[("Text files", "*.txt")]
    )
    if not file_paths:
        return

    save_dir = filedialog.askdirectory(title="Chọn thư mục lưu")
    if not save_dir:
        return

    for file_path in file_paths:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            merged = clean_mode_1(content)
            subbed = clean_mode_2(
                content,
                split_comma=split_comma_var.get(),
                split_period=split_period_var.get(),
                split_qe=split_qe_var.get()
            )

            base_name = os.path.basename(file_path)
            name, ext = os.path.splitext(base_name)

            merged_path = os.path.join(save_dir, f"{name}_merged{ext}")
            sub_path = os.path.join(save_dir, f"{name}_sub{ext}")

            with open(merged_path, "w", encoding="utf-8") as f:
                f.write(merged)
            with open(sub_path, "w", encoding="utf-8") as f:
                f.write(subbed)

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không xử lý được {file_path}\n{e}")
            return

    messagebox.showinfo(
        "Hoàn tất",
        f"✅ Đã xử lý {len(file_paths)} file.\n"
        f"Mỗi file gốc xuất ra 2 bản: <tên>_merged và <tên>_sub.\n"
        f"Kết quả lưu tại {save_dir}"
    )


# ================== GUI ==================
root = tk.Tk()
root.title("Làm sạch file TXT - Xuất 2 phiên bản")

frame = tk.Frame(root, padx=20, pady=20)
frame.pack()

label = tk.Label(frame, text="Chọn file TXT, chương trình sẽ xuất ra 2 phiên bản cho mỗi file:")
label.pack(pady=10)

# Checkbox bật/tắt tách sub tại dấu phẩy
split_comma_var = tk.BooleanVar(value=False)
chk_comma = tk.Checkbutton(frame, text="Tách sub tại dấu phẩy (, ， 、)", variable=split_comma_var)
chk_comma.pack(pady=5)

# Checkbox bật/tắt tách sub tại dấu chấm
split_period_var = tk.BooleanVar(value=True)
chk_period = tk.Checkbutton(frame, text="Tách sub tại dấu chấm (. 。 ．)", variable=split_period_var)
chk_period.pack(pady=5)

# Checkbox bật/tắt tách sub tại ? !
split_qe_var = tk.BooleanVar(value=True)
chk_qe = tk.Checkbutton(frame, text="Tách sub tại dấu ? và ! ( ? ! ？ ！ )", variable=split_qe_var)
chk_qe.pack(pady=5)

btn = tk.Button(frame, text="Chọn file và xử lý", command=process_files)
btn.pack(pady=10)

root.mainloop()

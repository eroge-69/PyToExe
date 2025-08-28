import os
import tkinter as tk
from tkinter import filedialog, messagebox
import zipfile
import re

def parse_time_to_seconds(timestr):
    h, m, s_ms = timestr.split(":")
    s, ms = s_ms.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0

def split_by_lines(blocks, line_count, base_name, folder):
    results = []
    file_index = 1
    for i in range(0, len(blocks), line_count):
        chunk = blocks[i:i + line_count]
        rebuilt = []
        for idx, block in enumerate(chunk, start=1):
            parts = block.splitlines()
            parts[0] = str(idx)
            rebuilt.append("\n".join(parts))
        rebuilt_text = "\n\n".join(rebuilt)
        filename = f"{base_name}P{file_index}.srt"
        out_path = os.path.join(folder, filename)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(rebuilt_text)
        results.append(out_path)
        file_index += 1
    return results

def split_by_time(blocks, seconds, base_name, folder):
    results = []
    file_index = 1
    current_chunk = []
    current_start = None

    for block in blocks:
        lines = block.splitlines()
        if len(lines) < 2:
            continue
        time_line = lines[1]
        start_time = time_line.split(" --> ")[0]
        start_sec = parse_time_to_seconds(start_time)

        if current_start is None:
            current_start = start_sec

        if start_sec - current_start >= seconds and current_chunk:
            rebuilt = []
            for idx, b in enumerate(current_chunk, start=1):
                parts = b.splitlines()
                parts[0] = str(idx)
                rebuilt.append("\n".join(parts))
            rebuilt_text = "\n\n".join(rebuilt)
            filename = f"{base_name}P{file_index}.srt"
            out_path = os.path.join(folder, filename)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(rebuilt_text)
            results.append(out_path)
            file_index += 1
            current_chunk = []
            current_start = start_sec

        current_chunk.append(block)

    if current_chunk:
        rebuilt = []
        for idx, b in enumerate(current_chunk, start=1):
            parts = b.splitlines()
            parts[0] = str(idx)
            rebuilt.append("\n".join(parts))
        rebuilt_text = "\n\n".join(rebuilt)
        filename = f"{base_name}P{file_index}.srt"
        out_path = os.path.join(folder, filename)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(rebuilt_text)
        results.append(out_path)
    return results

def split_by_parts(blocks, num_parts, base_name, folder):
    results = []
    total = len(blocks)
    size = total // num_parts
    file_index = 1
    for i in range(num_parts):
        start = i * size
        end = (i + 1) * size if i < num_parts - 1 else total
        chunk = blocks[start:end]
        rebuilt = []
        for idx, block in enumerate(chunk, start=1):
            parts = block.splitlines()
            parts[0] = str(idx)
            rebuilt.append("\n".join(parts))
        rebuilt_text = "\n\n".join(rebuilt)
        filename = f"{base_name}P{file_index}.srt"
        out_path = os.path.join(folder, filename)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(rebuilt_text)
        results.append(out_path)
        file_index += 1
    return results

def split_srt(file_path, mode, value, make_zip=True, preview=False):
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    folder = os.path.dirname(file_path)

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = [b for b in re.split(r"\n\s*\n", content) if b.strip()]

    if mode == "line":
        if preview:
            return (len(blocks) + int(value) - 1) // int(value)
        results = split_by_lines(blocks, int(value), base_name, folder)
        zip_name = f"{base_name}-{value}-line.zip"
    elif mode == "time":
        if preview:
            total_time = parse_time_to_seconds(blocks[-1].splitlines()[1].split(" --> ")[1])
            return (int(total_time) + int(value) - 1) // int(value)
        results = split_by_time(blocks, int(value), base_name, folder)
        zip_name = f"{base_name}-{value}-time.zip"
    else:  # parts
        if preview:
            return int(value)
        results = split_by_parts(blocks, int(value), base_name, folder)
        zip_name = f"{base_name}-{value}-parts.zip"

    if make_zip:
        zip_path = os.path.join(folder, zip_name)
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for f in results:
                zipf.write(f, os.path.basename(f))
        messagebox.showinfo("Hoàn tất", f"✅ Đã tách xong.\nFile ZIP lưu tại:\n{zip_path}")
    else:
        messagebox.showinfo("Hoàn tất", f"✅ Đã tách xong.\nCác file .srt đã lưu trong thư mục:\n{folder}")

# ---------------- GUI ----------------
def choose_file():
    file_path = filedialog.askopenfilename(filetypes=[("SRT files", "*.srt")])
    if file_path:
        entry_file.delete(0, tk.END)
        entry_file.insert(0, file_path)

        # Đếm số dòng subtitle
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        blocks = [b for b in re.split(r"\n\s*\n", content) if b.strip()]
        lbl_info.config(text=f"Tổng số dòng: {len(blocks)}", fg="blue")

def run_split():
    file_path = entry_file.get().strip()
    mode = mode_var.get()
    make_zip = zip_var.get()

    if not file_path or not os.path.exists(file_path):
        messagebox.showerror("Lỗi", "Chưa chọn file hợp lệ.")
        return

    if mode == "line":
        value = entry_line.get().strip()
        if not value.isdigit():
            messagebox.showerror("Lỗi", "Số dòng phải là số.")
            return
    elif mode == "time":
        h = entry_hour.get().strip() or "0"
        m = entry_minute.get().strip() or "0"
        if not h.isdigit() or not m.isdigit():
            messagebox.showerror("Lỗi", "Giờ và phút phải là số.")
            return
        value = int(h) * 3600 + int(m) * 60
        if value <= 0:
            messagebox.showerror("Lỗi", "Thời gian phải > 0.")
            return
    else:  # parts
        value = entry_parts.get().strip()
        if not value.isdigit() or int(value) <= 0 or int(value) > 9:
            messagebox.showerror("Lỗi", "Số phần phải từ 1 đến 9.")
            return

    num_files = split_srt(file_path, mode, value, preview=True)
    if num_files > 10:
        confirm = messagebox.askyesno("Cảnh báo", 
            "⚠️ SỐ FILE XUẤT RA KHÁ NHIỀU.\nBẠN CÓ CHẮC CHẮN CHỌN ĐÚNG KHÔNG?")
        if not confirm:
            return

    split_srt(file_path, mode, value, make_zip)

def run_preview():
    file_path = entry_file.get().strip()
    mode = mode_var.get()

    if not file_path or not os.path.exists(file_path):
        lbl_preview.config(text="⚠️ Chưa chọn file hợp lệ.", fg="red")
        return

    try:
        if mode == "line":
            value = entry_line.get().strip()
            if not value.isdigit():
                lbl_preview.config(text="⚠️ Số dòng phải là số.", fg="red")
                return
        elif mode == "time":
            h = entry_hour.get().strip() or "0"
            m = entry_minute.get().strip() or "0"
            if not h.isdigit() or not m.isdigit():
                lbl_preview.config(text="⚠️ Giờ và phút phải là số.", fg="red")
                return
            value = int(h) * 3600 + int(m) * 60
            if value <= 0:
                lbl_preview.config(text="⚠️ Thời gian phải > 0.", fg="red")
                return
        else:
            value = entry_parts.get().strip()
            if not value.isdigit() or int(value) <= 0 or int(value) > 9:
                lbl_preview.config(text="⚠️ Số phần phải từ 1 đến 9.", fg="red")
                return

        num_files = split_srt(file_path, mode, value, preview=True)
        text_msg = f"Sẽ tạo ra {num_files} file SRT."
        if num_files > 10:
            text_msg += " ⚠️ QUÁ NHIỀU FILE!"
        lbl_preview.config(text=text_msg, fg="blue")
    except Exception as e:
        lbl_preview.config(text=f"Lỗi preview: {e}", fg="red")

def update_fields():
    mode = mode_var.get()
    frame_line.grid_remove()
    frame_time.grid_remove()
    frame_parts.grid_remove()
    if mode == "line":
        frame_line.grid(row=2, column=0, columnspan=3, pady=5)
    elif mode == "time":
        frame_time.grid(row=2, column=0, columnspan=3, pady=5)
    else:
        frame_parts.grid(row=2, column=0, columnspan=3, pady=5)

# GUI setup
root = tk.Tk()
root.title("Tách file SRT")

tk.Button(root, text="Chọn file SRT:", command=choose_file).grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_file = tk.Entry(root, width=50)
entry_file.grid(row=0, column=1, padx=5, pady=5)
lbl_info = tk.Label(root, text="", fg="blue")
lbl_info.grid(row=0, column=2, padx=5, pady=5, sticky="w")

mode_var = tk.StringVar(value="line")
tk.Radiobutton(root, text="Theo số dòng", variable=mode_var, value="line", command=update_fields).grid(row=1, column=0, sticky="w", padx=5)
tk.Radiobutton(root, text="Theo thời gian (giờ/phút)", variable=mode_var, value="time", command=update_fields).grid(row=1, column=1, sticky="w", padx=5)
tk.Radiobutton(root, text="Chia đều số phần", variable=mode_var, value="parts", command=update_fields).grid(row=1, column=2, sticky="w", padx=5)

# Frame nhập số dòng
frame_line = tk.Frame(root)
tk.Label(frame_line, text="Số dòng:").pack(side="left", padx=5)
entry_line = tk.Entry(frame_line, width=10)
entry_line.pack(side="left")

# Frame nhập thời gian
frame_time = tk.Frame(root)
tk.Label(frame_time, text="Giờ:").pack(side="left")
entry_hour = tk.Entry(frame_time, width=5)
entry_hour.pack(side="left", padx=5)
tk.Label(frame_time, text="Phút:").pack(side="left")
entry_minute = tk.Entry(frame_time, width=5)
entry_minute.pack(side="left", padx=5)

# Frame nhập số phần
frame_parts = tk.Frame(root)
tk.Label(frame_parts, text="Số phần (≤9):").pack(side="left", padx=5)
entry_parts = tk.Entry(frame_parts, width=5)
entry_parts.pack(side="left")

update_fields()

zip_var = tk.BooleanVar(value=True)
tk.Checkbutton(root, text="Lưu file ZIP sau khi tách", variable=zip_var).grid(row=3, column=0, columnspan=3, sticky="w", padx=5, pady=5)

frame_buttons = tk.Frame(root)
frame_buttons.grid(row=4, column=0, columnspan=3, pady=10)
tk.Button(frame_buttons, text="Preview", command=run_preview, bg="lightyellow").pack(side="left", padx=10)
tk.Button(frame_buttons, text="Tách File", command=run_split, bg="lightblue").pack(side="left", padx=10)

lbl_preview = tk.Label(root, text="", fg="blue")
lbl_preview.grid(row=5, column=0, columnspan=3, pady=10)

root.mainloop()

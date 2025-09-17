import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import os
import random
import tempfile
import math

# 🔹 Đường dẫn FFmpeg cố định
FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"
FFPROBE_PATH = r"C:\ffmpeg\bin\ffprobe.exe"

# ---------------- Hàm xử lý video ----------------

def get_duration(input_file):
    input_file = os.path.normpath(input_file)
    result = subprocess.run(
        [FFPROBE_PATH, "-v", "error", "-show_entries",
         "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
         input_file],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    try:
        return float(result.stdout.strip())
    except:
        return 0.0

def cut_random_segment(input_file, output_file, flip_mode="none"):
    try:
        input_file = os.path.normpath(input_file)
        output_file = os.path.normpath(output_file)

        duration = get_duration(input_file)
        if duration <= 2.15:
            start_time = 0
        else:
            start_time = random.uniform(0, duration - 2.15)

        tmp_cut = output_file.replace(".mp4", "_cut.mp4")

        # B1: cắt 2.15s
        subprocess.run([
            FFMPEG_PATH, "-y", "-ss", str(start_time), "-i", input_file,
            "-t", "2.15", "-c:v", "libx264", "-c:a", "aac", tmp_cut
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # B2: scale 110% + flip
        vf_filter = "scale=iw*1.1:ih*1.1"
        if flip_mode == "hflip":
            vf_filter += ",hflip"
        elif flip_mode == "vflip":
            vf_filter += ",vflip"

        subprocess.run([
            FFMPEG_PATH, "-y", "-i", tmp_cut,
            "-vf", vf_filter, "-c:v", "libx264",
            "-c:a", "aac", output_file
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if os.path.exists(tmp_cut):
            os.remove(tmp_cut)

    except Exception as e:
        print(f"Lỗi cắt video {input_file}: {e}")

def export_video(files, output_name, num_videos, flip_mode, transition, save_dir):
    try:
        for vid_index in range(num_videos):
            with tempfile.TemporaryDirectory() as tmpdir:
                cut_files = []

                # Xáo trộn 6 video đầu vào
                random.shuffle(files)

                for i, f in enumerate(files):
                    cut_file = os.path.join(tmpdir, f"cut_{i}.mp4")
                    cut_random_segment(f, cut_file, flip_mode)
                    cut_files.append(cut_file)

                total_len = len(cut_files) * 2.15
                need_repeat = math.ceil(20 / total_len)
                cut_files = cut_files * need_repeat

                needed_segments = int(20 / 2.15)
                cut_files = cut_files[:needed_segments]

                random.shuffle(cut_files)

                list_file = os.path.join(tmpdir, "list.txt")
                with open(list_file, "w", encoding="utf-8") as f:
                    for cf in cut_files:
                        f.write(f"file '{os.path.normpath(cf)}'\n")

                out_file = os.path.join(save_dir, f"{output_name}_{vid_index+1}.mp4")

                # Nếu chọn xfade, dùng filter_complex
                if transition != "none":
                    # Xây dựng filter cho xfade giữa các đoạn
                    filter_cmd = ""
                    input_cmds = []
                    for idx, cf in enumerate(cut_files):
                        input_cmds.extend(["-i", cf])
                    # Xfade duration = 0.5s
                    dur_per_clip = 2.15
                    filter_lines = []
                    vprev = "[0:v]"
                    aprev = "[0:a]"
                    for i in range(1, len(cut_files)):
                        vnext = f"[{i}:v]"
                        anext = f"[{i}:a]"
                        vout = f"[v{i}]"
                        aout = f"[a{i}]"
                        filter_lines.append(f"{vprev}{vnext} xfade=transition={transition}:duration=0.5:offset={i*dur_per_clip} {vout}; {aprev}{anext} acrossfade=d=0.5 {aout}")
                        vprev = vout
                        aprev = aout
                    filter_complex = "; ".join(filter_lines)

                    cmd = [FFMPEG_PATH, "-y"]
                    cmd += input_cmds
                    cmd += ["-filter_complex", filter_complex, "-map", vprev, "-map", aprev, out_file]
                    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                else:
                    cmd = [FFMPEG_PATH, "-y", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", out_file]
                    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        messagebox.showinfo("Hoàn thành", f"Đã xuất {num_videos} video thành công!")

    except Exception as e:
        messagebox.showerror("Lỗi", f"Xuất video thất bại: {e}")

# ---------------- Giao diện Tkinter ----------------

root = tk.Tk()
root.title("Video Cutter & Merger (FFmpeg)")

files = []

# Chọn file
def select_files():
    filenames = filedialog.askopenfilenames(
        title="Chọn video",
        filetypes=[("Video files", "*.mp4 *.mov *.avi *.mkv")]
    )
    if filenames:
        files.clear()
        file_listbox.delete(0, tk.END)
        for f in filenames:
            files.append(f)
            file_listbox.insert(tk.END, f)

def select_save_dir():
    path = filedialog.askdirectory(title="Chọn thư mục lưu video")
    if path:
        save_dir_var.set(path)

def start_export():
    if not files:
        messagebox.showwarning("Cảnh báo", "Chưa chọn video đầu vào!")
        return

    output_name = output_entry.get().strip()
    if not output_name:
        output_name = "output"

    num_videos = int(num_videos_spin.get())
    flip_mode = flip_var.get()
    transition = transition_var.get()
    save_dir = save_dir_var.get()
    if not save_dir:
        messagebox.showwarning("Cảnh báo", "Chưa chọn thư mục lưu video!")
        return

    export_video(files, output_name, num_videos, flip_mode, transition, save_dir)

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

btn_select = tk.Button(frame, text="Chọn Video", command=select_files)
btn_select.grid(row=0, column=0, pady=5)

file_listbox = tk.Listbox(frame, width=80, height=6)
file_listbox.grid(row=1, column=0, columnspan=3, pady=5)

# Tên file xuất
tk.Label(frame, text="Tên file xuất:").grid(row=2, column=0, sticky="w")
output_entry = tk.Entry(frame, width=30)
output_entry.grid(row=2, column=1, pady=5)

# Thư mục lưu
tk.Label(frame, text="Thư mục lưu:").grid(row=3, column=0, sticky="w")
save_dir_var = tk.StringVar(master=root)
save_dir_entry = tk.Entry(frame, textvariable=save_dir_var, width=30)
save_dir_entry.grid(row=3, column=1, pady=5)
btn_save_dir = tk.Button(frame, text="Chọn...", command=select_save_dir)
btn_save_dir.grid(row=3, column=2, padx=5)

# Số video xuất
tk.Label(frame, text="Số video xuất:").grid(row=4, column=0, sticky="w")
num_videos_spin = tk.Spinbox(frame, from_=1, to=10, width=5)
num_videos_spin.grid(row=4, column=1, sticky="w")

# Flip
tk.Label(frame, text="Hiệu ứng Flip:").grid(row=5, column=0, sticky="w")
flip_var = tk.StringVar(value="none")
flip_menu = ttk.Combobox(frame, textvariable=flip_var, values=["none", "hflip", "vflip"])
flip_menu.grid(row=5, column=1, pady=5)

# Transition
tk.Label(frame, text="Hiệu ứng chuyển cảnh:").grid(row=6, column=0, sticky="w")
transition_var = tk.StringVar(value="none")
transition_menu = ttk.Combobox(frame, textvariable=transition_var, values=["none","fade","wipeleft","wiperight","fadeblack","dissolve"])
transition_menu.grid(row=6, column=1, pady=5)

btn_export = tk.Button(frame, text="Xuất Video", command=start_export)
btn_export.grid(row=7, column=0, columnspan=2, pady=10)

root.mainloop()

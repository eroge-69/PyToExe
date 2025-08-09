import os
import subprocess
import tkinter as tk
from tkinter import filedialog
from PIL import Image
from datetime import datetime

# === Kiểm tra hạn sử dụng tool (ẩn) ===
def check_expiry():
    # Ngày hết hạn key (định dạng: YYYY-MM-DD)
    expiry_str = "2025-08-11"  # <-- sửa thành ngày bạn muốn
    expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
    today = datetime.now().date()

    if today > expiry_date:
        print("🛠️ Tool đang cập nhật, quý khách vui lòng đợi...")
        raise SystemExit

check_expiry()  # Gọi hàm kiểm tra hạn

# === Hàm chọn file ===
def pick_file(title, filetypes):
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(title=title, filetypes=filetypes)

# === Hàm chọn thư mục lưu ===
def pick_folder():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askdirectory(title="Chọn thư mục lưu video")

# === Resize ảnh về 1920x1080 ===
def resize_to_1080p(img_path):
    img = Image.open(img_path)
    img_ratio = img.width / img.height
    target_ratio = 1920 / 1080
    if img_ratio > target_ratio:
        new_height = 1080
        new_width = int(1080 * img_ratio)
    else:
        new_width = 1920
        new_height = int(1920 / img_ratio)
    resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    left = (new_width - 1920) // 2
    top = (new_height - 1080) // 2
    right = left + 1920
    bottom = top + 1080
    cropped_img = resized_img.crop((left, top, right, bottom))
    output_path = os.path.join(os.path.dirname(img_path), "resized_image.png")
    cropped_img.save(output_path)
    return output_path

# === Lấy thời lượng audio ===
def get_audio_duration(audio_file):
    cmd = [
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration", "-of",
        "default=noprint_wrappers=1:nokey=1", audio_file
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return float(result.stdout)

# === Nhập dữ liệu từ người dùng ===
print("🖼 Chọn ảnh hoặc video nền:")
bg_input_path = pick_file("Chọn ảnh hoặc video nền", [("Media files", "*.png *.jpg *.jpeg *.mp4")])
if not bg_input_path:
    raise SystemExit("❌ Không chọn file nền!")

is_video_background = bg_input_path.lower().endswith(".mp4")

print("🎤 Chọn video MC (không nền):")
mc_path = pick_file("Chọn video MC", [("Video", "*.mp4")])
if not mc_path:
    raise SystemExit("❌ Không chọn file MC!")

print("✨ Chọn hiệu ứng overlay (hoặc bỏ qua):")
effect_path = pick_file("Chọn hiệu ứng overlay", [("Video", "*.mp4")])
use_effect = bool(effect_path)

print("🔊 Chọn file âm thanh (.mp3):")
audio_path = pick_file("Chọn âm thanh", [("MP3", "*.mp3")])
if not audio_path:
    raise SystemExit("❌ Không chọn âm thanh!")

audio_duration = get_audio_duration(audio_path)

# Nhập chữ chạy
scroll_text = input("📝 Nhập dòng chữ chạy ngang: ").strip()
if not scroll_text:
    scroll_text = " "  # tránh filter rỗng
# Escape để tránh FFmpeg hiểu sai
scroll_text_escaped = scroll_text.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")

# Cỡ chữ
font_size = input("🔠 Nhập cỡ chữ (ví dụ 40): ").strip()
if not font_size.isdigit():
    font_size = "40"

# Thêm nhiễu?
add_noise = input("🌪️ Thêm hiệu ứng nhiễu? (y/n): ").strip().lower() == "y"

# Số luồng CPU
threads = input("⚙️ Nhập số luồng CPU (Enter để tự động): ").strip()
if not threads.isdigit():
    threads = None

# Font path
FONT_PATH = "C\\:/Windows/Fonts/arial.ttf"  
# Chọn thư mục lưu
save_folder = pick_folder()
if not save_folder:
    raise SystemExit("❌ Không chọn thư mục lưu!")

# Tạo tên file tăng dần
i = 1
while True:
    save_path = os.path.join(save_folder, f"video{i}.mp4")
    if not os.path.exists(save_path):
        break
    i += 1

# Tạo video nền
video_base = "video_base.mp4"
if is_video_background:
    cmd_loop_video = [
        "ffmpeg", "-y", "-stream_loop", "-1", "-i", bg_input_path,
        "-i", audio_path,
        "-t", str(audio_duration),
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-c:a", "aac",
        "-pix_fmt", "yuv420p", "-shortest", video_base
    ]
else:
    bg_image_resized = resize_to_1080p(bg_input_path)
    cmd_loop_video = [
        "ffmpeg", "-y", "-loop", "1", "-i", bg_image_resized,
        "-i", audio_path, "-c:v", "libx264", "-tune", "stillimage",
        "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p",
        "-t", str(audio_duration), "-shortest", video_base
    ]
subprocess.run(cmd_loop_video)

# Inputs
inputs = ["-i", video_base, "-stream_loop", "-1", "-i", mc_path]
if use_effect:
    inputs += ["-stream_loop", "-1", "-i", effect_path]

# Filter
filter_chain = ""
if use_effect:
    filter_chain += "[2:v]colorkey=0x01ff11:0.3:0.1[fx];"
    filter_chain += "[0:v][fx]overlay=0:0[tmp];"
    base = "[tmp]"
else:
    base = "[0:v]"

filter_chain += "[1:v]colorkey=0x01ff11:0.3:0.2,scale=480:-1[ckout];"
filter_chain += f"{base}[ckout]overlay=50:H-h[out1];"

filter_chain += (
    f"[out1]drawtext=fontfile='{FONT_PATH}':text='{scroll_text_escaped}':"
    f"fontcolor=yellow:fontsize={font_size}:x=w-mod(t*200\,w+tw):"
    f"y=50:box=1:boxcolor=black@1[out2]"
)
if add_noise:
    filter_chain += ";[out2]noise=alls=20:allf=t[outv]"
    output_map = "[outv]"
else:
    output_map = "[out2]"

# Xuất video
cmd_final = ["ffmpeg", "-y"] + inputs + [
    "-filter_complex", filter_chain,
    "-map", output_map, "-map", "0:a",
    "-c:v", "libx264", "-preset", "fast", "-crf", "30",
    "-c:a", "aac", "-b:a", "192k",
    "-movflags", "+faststart",
    "-shortest", save_path
]



if threads:
    cmd_final += ["-threads", threads]

print(f"🎬 Đang xuất video ({save_path}) ...")
subprocess.run(cmd_final)
print(f"✅ Video đã tạo: {save_path}")

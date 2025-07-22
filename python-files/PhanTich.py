import os
import zipfile
import tempfile
from pathlib import Path
from moviepy.editor import VideoFileClip
from tabulate import tabulate
from concurrent.futures import ThreadPoolExecutor, as_completed

IMAGE_EXT = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
VIDEO_EXT = {'.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv', '.webm'}
COLOR_SEQ = ['\033[91m', '\033[93m', '\033[92m', '\033[96m', '\033[94m', '\033[95m']
RESET = '\033[0m'

def color_text(text, mode='cycle'):
    if mode == 'cycle':
        return ''.join(COLOR_SEQ[i % len(COLOR_SEQ)] + c for i, c in enumerate(text)) + RESET
    if mode == 'line':
        color = COLOR_SEQ[hash(text) % len(COLOR_SEQ)]
        return f"{color}{text}{RESET}"
    return text

def format_size(size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"

def format_duration(seconds):
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    return f"{h:02}:{m:02}:{s:02}"

def process_file(fp, base):
    try:
        ext = Path(fp).suffix.lower()
        rel_path = os.path.relpath(fp, base)
        if ext in IMAGE_EXT:
            return ('img', (rel_path, os.path.getsize(fp)))
        elif ext in VIDEO_EXT:
            size = os.path.getsize(fp)
            clip = VideoFileClip(fp)
            duration = clip.duration
            clip.close()
            return ('vid', (rel_path, duration, size))
    except:
        return None

def scan(path):
    files = []
    for root, _, fs in os.walk(path):
        for f in fs:
            files.append(os.path.join(root, f))
    
    images, videos = [], []
    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = {executor.submit(process_file, f, path): f for f in files}
        for future in as_completed(futures):
            result = future.result()
            if result:
                if result[0] == 'img':
                    images.append(result[1])
                elif result[0] == 'vid':
                    videos.append(result[1])
    return images, videos

def show(images, videos):
    if images:
        table = [[color_text(name), format_size(sz)] for name, sz in images]
        print(color_text("\nẢNH:", 'line'))
        print(tabulate(table, headers=[color_text("Tên ảnh"), color_text("Dung lượng")], tablefmt="fancy_grid"))
    print(color_text(f"==> Tổng ảnh: {len(images)} | Dung lượng: {format_size(sum(i[1] for i in images))}\n", 'line'))

    if videos:
        table = [[color_text(name), format_duration(dur), format_size(sz)] for name, dur, sz in videos]
        print(color_text("VIDEO:", 'line'))
        print(tabulate(table, headers=[color_text("Tên video"), color_text("Thời lượng"), color_text("Dung lượng")], tablefmt="fancy_grid"))
    print(color_text(f"==> Tổng video: {len(videos)} | Thời lượng: {format_duration(sum(v[1] for v in videos))} | Dung lượng: {format_size(sum(v[2] for v in videos))}", 'line'))

def process(p):
    if not p:
        p = "."
    if os.path.isfile(p) and p.lower().endswith(".zip"):
        with tempfile.TemporaryDirectory() as tmp:
            with zipfile.ZipFile(p) as z:
                z.extractall(tmp)
            i, v = scan(tmp)
    elif os.path.isdir(p):
        i, v = scan(p)
    else:
        print("Đường dẫn không hợp lệ.")
        return
    show(i, v)

if __name__ == "__main__":
    print(color_text("📂 Nhập đường dẫn thư mục hoặc file .zip", 'line'))
    print(color_text("↪ Nhấn Enter để quét toàn bộ thư mục hiện tại\n", 'line'))
    user_input = input(">>> ").strip()
    process(user_input)

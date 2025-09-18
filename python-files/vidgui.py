import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os

# Import your video processing logic
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip, ColorClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import math

# ==== DEFAULT CONFIG ====
VIDEO_PATH = ""
OUTPUT_FOLDER = ""
OVERLAY_PNG_PATH = ""
FONT_PATH = "arial.ttf"  # Adjust as needed
PART_DURATION = 60  # seconds
INTRO_RANGE = "none"
OUTRO_RANGE = "none"


# ========== Helper Functions ==========
def mmss_to_seconds(time_str):
    if ":" not in time_str:
        return float(time_str)
    minutes, seconds = map(int, time_str.split(":"))
    return minutes * 60 + seconds

def parse_time_range(range_str, total_duration):
    if not range_str or range_str.lower() == "none":
        return None
    parts = range_str.split("-")
    if len(parts) == 2:
        return mmss_to_seconds(parts[0]), mmss_to_seconds(parts[1])
    elif len(parts) == 1:
        return mmss_to_seconds(parts[0]), total_duration
    return None

def create_text_img(text, font_path, font_size, color, size, y_offset=0):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(font_path, font_size)
    except Exception:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    position = ((size[0] - w) // 2, y_offset)
    draw.text(position, text, font=font, fill=color)
    return np.array(img)


# ========== Video Processor ==========
def process_video(video_path, output_folder, logo_path):
    movie_name = os.path.splitext(os.path.basename(video_path))[0]
    full_clip = VideoFileClip(video_path)
    duration = full_clip.duration

    intro = parse_time_range(INTRO_RANGE, duration)
    outro = parse_time_range(OUTRO_RANGE, duration)
    clip_start = intro[1] if intro else 0
    clip_end = outro[0] if outro else duration
    if clip_end <= clip_start:
        raise ValueError("Clip end time must be greater than start time.")

    clip = full_clip.subclip(clip_start, clip_end)
    total_duration = clip.duration
    num_parts = math.ceil(total_duration / PART_DURATION)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    w_9, h_16 = 1080, 1920

    for i in range(num_parts):
        start = i * PART_DURATION
        end = min((i + 1) * PART_DURATION, total_duration)
        subclip = clip.subclip(start, end)

        aspect_ratio = subclip.w / subclip.h
        target_w = w_9
        target_h = int(w_9 / aspect_ratio)
        if target_h > h_16:
            target_h = h_16
            target_w = int(h_16 * aspect_ratio)

        resized_clip = subclip.resize(height=target_h if target_h < h_16 else h_16)
        x_pos = (w_9 - resized_clip.w) // 2
        y_pos = (h_16 - resized_clip.h) // 2

        title_img = create_text_img(
            movie_name, FONT_PATH, 80, "white", (w_9, 150), y_offset=30
        )
        part_img = create_text_img(
            f"Part {i+1}", FONT_PATH, 60, "white", (w_9, 100), y_offset=10
        )

        title_clip = ImageClip(title_img).set_duration(subclip.duration).set_position(("center", 30))
        part_clip = ImageClip(part_img).set_duration(subclip.duration).set_position(("center", y_pos + resized_clip.h + 20))
        logo_clip = ImageClip(logo_path).resize(width=300).set_duration(subclip.duration).set_position(("center", y_pos + resized_clip.h + 120))

        final = CompositeVideoClip([
            ColorClip((w_9, h_16), color=(0, 0, 0)).set_duration(subclip.duration),
            resized_clip.set_position((x_pos, y_pos)),
            title_clip,
            part_clip,
            logo_clip
        ], size=(w_9, h_16))

        output_name = f"{movie_name.strip()}-part_{i+1}.mp4"
        output_path = os.path.join(output_folder, output_name)
        print(f"🚀 Exporting: {output_path}")
        final.write_videofile(
            output_path,
            fps=25,
            threads=8,
            codec="libx264",
            audio_codec="aac",
            preset="ultrafast"
        )

    messagebox.showinfo("Done", "✅ All parts successfully exported!")


# ========== GUI ==========
def start_processing():
    video_path = video_entry.get().strip()
    output_folder = output_entry.get().strip()
    logo_path = logo_entry.get().strip()

    if not video_path or not output_folder or not logo_path:
        messagebox.showerror("Error", "Please select all inputs")
        return

    threading.Thread(target=process_video, args=(video_path, output_folder, logo_path), daemon=True).start()


def browse_video():
    filename = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.mkv *.avi")])
    if filename:
        video_entry.delete(0, tk.END)
        video_entry.insert(0, filename)

def browse_output():
    folder = filedialog.askdirectory()
    if folder:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, folder)

def browse_logo():
    filename = filedialog.askopenfilename(filetypes=[("PNG Files", "*.png")])
    if filename:
        logo_entry.delete(0, tk.END)
        logo_entry.insert(0, filename)


root = tk.Tk()
root.title("Video Splitter GUI")
root.geometry("600x300")

tk.Label(root, text="Source Video:").pack(anchor="w", padx=10, pady=5)
video_entry = tk.Entry(root, width=60)
video_entry.pack(padx=10)
tk.Button(root, text="Browse", command=browse_video).pack(pady=5)

tk.Label(root, text="Output Folder:").pack(anchor="w", padx=10, pady=5)
output_entry = tk.Entry(root, width=60)
output_entry.pack(padx=10)
tk.Button(root, text="Browse", command=browse_output).pack(pady=5)

tk.Label(root, text="Logo (PNG):").pack(anchor="w", padx=10, pady=5)
logo_entry = tk.Entry(root, width=60)
logo_entry.pack(padx=10)
tk.Button(root, text="Browse", command=browse_logo).pack(pady=5)

tk.Button(root, text="Start Processing", command=start_processing, bg="green", fg="white").pack(pady=20)

root.mainloop()

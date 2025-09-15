import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
import tempfile

def get_video_info(file_path):
    import json
    try:
        cmd = [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height,r_frame_rate",
            "-of", "json", file_path
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        info = json.loads(result.stdout)
        stream = info.get("streams", [])[0]
        width = stream.get("width")
        height = stream.get("height")
        fps_str = stream.get("r_frame_rate", "0/1")
        num, den = map(int, fps_str.split("/"))
        fps = num / den if den != 0 else 0
        return width, height, fps
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read video info: {e}")
        return None, None, 0

def process_video(input_path, output_path):
    width, height, fps = get_video_info(input_path)

    filters = []
    if fps < 60:
        filters.append("minterpolate=fps=60:mi_mode=mci:mc_mode=obmc:me_mode=bidir:scd=itscale=2")
    elif fps > 60:
        filters.append("fps=60")

    vf = ",".join(filters) if filters else None

    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".mp4")
    os.close(tmp_fd)

    crf = 23
    input_size = os.path.getsize(input_path)
    output_size = input_size + 1

    while output_size >= input_size and crf < 40:
        try:
            cmd = ["ffmpeg", "-y", "-i", input_path]
            if vf:
                cmd += ["-vf", vf]
            cmd += [
                "-c:v", "libx264", "-crf", str(crf), "-preset", "fast",
                "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k",
                "-movflags", "+faststart", tmp_path
            ]
            subprocess.run(cmd, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            output_size = os.path.getsize(tmp_path)
            if output_size >= input_size:
                crf += 2
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Encoding failed: {e}")
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            return

    shutil.move(tmp_path, output_path)

def main():
    root = tk.Tk()
    root.withdraw()

    # Intro popup
    intro = tk.Toplevel()
    intro.title("Info")
    tk.Label(intro, text="Method By cark12345 On Discord.", font=("Arial", 12)).pack(padx=20, pady=10)
    tk.Button(intro, text="OK", command=intro.destroy).pack(pady=10)
    intro.transient(root)
    intro.grab_set()
    root.wait_window(intro)

    # Select input file
    input_path = filedialog.askopenfilename(title="Select input video", filetypes=[("Video files", "*.mp4;*.mov;*.mkv;*.avi")])
    if not input_path or not os.path.isfile(input_path):
        messagebox.showerror("Error", "No valid input file selected.")
        return

    if os.path.splitext(os.path.basename(input_path))[0].lower() != "input":
        messagebox.showerror("Error", "The file must be named 'input'.")
        return

    output_dir = os.path.dirname(input_path)
    output_path = os.path.join(output_dir, "output.mp4")

    process_video(input_path, output_path)

    # Completion popup
    done = tk.Toplevel()
    done.title("Completed")
    tk.Label(done, text="Video Completed.", font=("Arial", 12)).pack(padx=20, pady=10)
    tk.Button(done, text="OK", command=done.destroy).pack(pady=10)
    done.transient(root)
    done.grab_set()
    root.wait_window(done)

    # Open folder containing output
    if os.name == "nt":
        subprocess.run(["explorer", "/select,", output_path], creationflags=subprocess.CREATE_NO_WINDOW)
    elif os.name == "posix":
        subprocess.run(["xdg-open", output_dir])

if __name__ == "__main__":
    main()

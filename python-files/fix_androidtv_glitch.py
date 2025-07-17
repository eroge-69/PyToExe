
import os
import subprocess

def fix_android_tv_glitch(input_path, output_path):
    """
    Re-encodes a glitched video to fix Android TV green line issue.
    Adjusts width to safe resolution (e.g., 768 or 1280), uses yuv420p, and pads if needed.
    """
    try:
        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-vf", (
                # Normalize dimensions to safe range
                "crop='trunc(iw/2)*2:trunc(ih/2)*2',"       # Ensure even
                "scale=768:1152,"                           # 🔁 Resize to safe dimensions (taller but narrow)
                "pad=768:1154:0:0:color=black"              # 🔲 Add 2px bottom padding to avoid overflow
            ),
            "-c:v", "libx264",
            "-profile:v", "high",
            "-level", "4.0",
            "-pix_fmt", "yuv420p",
            "-preset", "slow",
            "-crf", "22",
            "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart",
            output_path
        ]
        subprocess.run(cmd, check=True)
        print(f"[✓] Fixed: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"[✗] FFmpeg error: {e}")

def process_file(input_file, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    filename = os.path.splitext(os.path.basename(input_file))[0]
    output_file = os.path.join(output_folder, f"{filename}_tvfixed.mp4")
    fix_android_tv_glitch(input_file, output_file)

if __name__ == "__main__":
    # 👇 Change this path to your glitched video
    input_video = "/Users/surajkakade/Downloads/1752477471_6aa99234753ff048adf2.mp4"
    output_dir = "processed_videos"
    process_file(input_video, output_dir)

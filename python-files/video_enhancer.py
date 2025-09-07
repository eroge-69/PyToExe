import os
import subprocess
import sys

def find_ffmpeg():
    """Check if ffmpeg.exe is in the same folder as this script/exe."""
    local_ffmpeg = os.path.join(os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else _file_), "ffmpeg.exe")
    if os.path.isfile(local_ffmpeg):
        return local_ffmpeg
    else:
        print("⚠️ ffmpeg.exe not found! Please download it and place it in the same folder as this program.")
        input("Press Enter to exit...")
        sys.exit(1)

def enhance_videos():
    ffmpeg = find_ffmpeg()

    # Find all .mp4 files in the folder (ignore already enhanced files)
    files = [f for f in os.listdir('.') if f.lower().endswith('.mp4') and not f.startswith('Enhanced_')]
    if not files:
        print("⚠️ No input videos found! Place your .mp4 files in the same folder as this program.")
        input("Press Enter to exit...")
        return

    print(f"🎬 Found {len(files)} video(s): {', '.join(files)}")

    # Video enhancement filters: denoise + sharpen
    vf_filter = "hqdn3d=1.5:1.5:6:6,unsharp=5:5:0.8:5:5:0.4"

    for input_file in files:
        base_name = os.path.splitext(input_file)[0]
        output_1080p = f"{base_name}_Enhanced_1080p.mp4"
        output_4k = f"{base_name}_Enhanced_4K.mp4"

        print(f"\n▶ Processing {input_file}...")

        # 1080p version
        print("   🔄 Creating 1080p version...")
        subprocess.run([
            ffmpeg, "-i", input_file,
            "-vf", f"scale=-2:1080,{vf_filter}",
            "-c:v", "libx264", "-preset", "slow", "-b:v", "6M",
            "-c:a", "aac", "-b:a", "192k",
            output_1080p, "-y"
        ])

        # 4K version
        print("   🔄 Creating 4K version...")
        subprocess.run([
            ffmpeg, "-i", input_file,
            "-vf", f"scale=-2:2160,{vf_filter}",
            "-c:v", "libx264", "-preset", "slow", "-b:v", "20M",
            "-c:a", "aac", "-b:a", "192k",
            output_4k, "-y"
        ])

        print(f"   ✅ Done: {output_1080p}, {output_4k}")

    print("\n🎉 All videos processed successfully!")
    input("Press Enter to exit...")

if _name_ == "_main_":
    enhance_videos()
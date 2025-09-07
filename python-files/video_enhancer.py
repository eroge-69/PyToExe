import os
import subprocess

def enhance_video():
    # Find the first .mp4 file in the folder
    files = [f for f in os.listdir('.') if f.lower().endswith('.mp4') and not f.startswith('Enhanced_')]
    if not files:
        print("⚠️ No input video found! Please place your video file in the same folder as this program.")
        input("Press Enter to exit...")
        return

    input_file = files[0]
    print(f"🎬 Found video: {input_file}")

    # Output files
    output_1080p = "Enhanced_1080p.mp4"
    output_4k = "Enhanced_4K.mp4"

    # Common ffmpeg filter: denoise + sharpen
    vf_filter = "hqdn3d=1.5:1.5:6:6,unsharp=5:5:0.8:5:5:0.4"

    # 1080p version
    print("🔄 Creating 1080p version...")
    subprocess.run([
        "ffmpeg", "-i", input_file,
        "-vf", f"scale=-2:1080,{vf_filter}",
        "-c:v", "libx264", "-preset", "slow", "-b:v", "6M",
        "-c:a", "aac", "-b:a", "192k",
        output_1080p, "-y"
    ])

    # 4K version
    print("🔄 Creating 4K version...")
    subprocess.run([
        "ffmpeg", "-i", input_file,
        "-vf", f"scale=-2:2160,{vf_filter}",
        "-c:v", "libx264", "-preset", "slow", "-b:v", "20M",
        "-c:a", "aac", "-b:a", "192k",
        output_4k, "-y"
    ])

    print("\n✅ Done! Check the folder for:")
    print(f"   → {output_1080p}")
    print(f"   → {output_4k}")
    input("\nPress Enter to exit...")

if _name_ == "_main_":
    enhance_video()
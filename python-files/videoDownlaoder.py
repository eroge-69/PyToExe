import yt_dlp
import os
import shutil

def download_video(url, download_path):
    # Detect if ffmpeg is installed
    ffmpeg_installed = shutil.which("ffmpeg") is not None

    if ffmpeg_installed:
        ydl_opts = {
            "outtmpl": os.path.join(download_path, "%(title)s.%(ext)s"),
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
            "noplaylist": True,
            "continuedl": True,  # Resume if interrupted
            "quiet": False
        }
    else:
        ydl_opts = {
            "outtmpl": os.path.join(download_path, "%(title)s.%(ext)s"),
            "format": "best",
            "noplaylist": True,
            "continuedl": True,
            "quiet": False
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("\n✅ Download complete!\n")
    except Exception as e:
        print("\n❌ The video not found, link error, or video is private.\n")

def main():
    print("\n==== Auto Video Downloader by @MullaRohan ====")
    print("Supports Facebook, YouTube, and more.")
    download_path = r"C:\Users\mdroh\Downloads"

    while True:
        url = input("\nEnter video link (or type 'exit' to quit): ").strip()
        if url.lower() == "exit":
            print("👋 Exiting downloader. Goodbye!")
            break

        print("\n⏳ Downloading video...")
        download_video(url, download_path)

if __name__ == "__main__":
    main()

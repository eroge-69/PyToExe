from pytube import YouTube

def download_video(url):
    try:
        yt = YouTube(url)
        stream = yt.streams.get_highest_resolution()
        print(f"\nVideo Title: {yt.title}")
        print("Downloading...")
        stream.download()
        print("✅ Download complete!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("=== YouTube Video Downloader ===")
    video_url = input("Enter YouTube Video URL: ").strip()
    if video_url:
        download_video(video_url)
    else:
        print("❗ No URL provided.")

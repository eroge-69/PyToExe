import requests

def download_tiktok(url, mode="mp4"):
    api_url = "https://ssstik.io/abc"
    headers = {"User-Agent": "Mozilla/5.0"}
    payload = {"id": url, "locale": "en", "tt": "some_token"}

    print("Processing TikTok link...")
    response = requests.post(api_url, headers=headers, data=payload)
    response.raise_for_status()

    html = response.text

    if mode == "mp4":
        # Try to find "without watermark" link
        try:
            download_link = html.split('without watermark')[1].split('href="')[1].split('"')[0]
            filename = "tiktok_video.mp4"
        except Exception:
            print("⚠️ Could not find MP4 link — TikTok page structure might’ve changed.")
            return
    elif mode == "mp3":
        # Try to find "MP3" link
        try:
            download_link = html.split('MP3')[1].split('href="')[1].split('"')[0]
            filename = "tiktok_audio.mp3"
        except Exception:
            print("⚠️ Could not find MP3 link — TikTok page structure might’ve changed.")
            return
    else:
        print("❌ Invalid mode selected.")
        return

    print(f"Downloading {mode.upper()}...")
    file_data = requests.get(download_link)
    with open(filename, "wb") as f:
        f.write(file_data.content)

    print(f"✅ Done! Saved as {filename}")


if __name__ == "__main__":
    print("🎧 TikTok Downloader (MP4 + MP3)")
    tiktok_url = input("Paste TikTok link: ")
    choice = input("Download as MP4 (video) or MP3 (audio)? ").strip().lower()
    if choice not in ["mp4", "mp3"]:
        print("⚠️ Please type only 'mp4' or 'mp3'")
    else:
        download_tiktok(tiktok_url, choice)

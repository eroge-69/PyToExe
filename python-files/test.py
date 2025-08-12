#請使用 Python，產生下載 Youtube 影片為 mp4的程式碼，使用者可以自行輸入網址

import yt_dlp

def download_youtube_mp4(url: str, output_path: str = "%(title)s.%(ext)s"):
    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": output_path,
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": False,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

if __name__ == "__main__":
    video_url = input("請輸入 YouTube 影片網址：")
    download_youtube_mp4(video_url)
    print("下載完成！")

import re
import requests

def get_video_id(url: str) -> str:
    """
    YouTube linkinden video ID'sini çıkarır.
    """
    match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url)
    if not match:
        raise ValueError("Video ID bulunamadı. Lütfen geçerli bir YouTube linki girin.")
    return match.group(1)

def get_dislike_data(video_url: str) -> dict:
    """
    Return YouTube Dislike API'dan verileri çeker.
    """
    video_id = get_video_id(video_url)
    api_url = f"https://returnyoutubedislikeapi.com/votes?videoId={video_id}"

    try:
        response = requests.get(api_url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return {
            "videoId": video_id,
            "title": data.get("title", "Bilinmiyor"),
            "likes": data.get("likes", 0),
            "dislikes": data.get("dislikes", 0),
            "views": data.get("viewCount", 0),
            "date": data.get("dateCreated", "Bilinmiyor")
        }
    except requests.RequestException as e:
        raise SystemError(f"API isteği başarısız: {e}")

if __name__ == "__main__":
    print("📺 YouTube Dislike Gösterici")
    video_link = input("Video linkini gir: ").strip()
    try:
        result = get_dislike_data(video_link)
        print("\n🔍 Video Bilgileri:")
        print(f"📌 Video ID: {result['videoId']}")
        print(f"📅 Tarih: {result['date']}")
        print(f"👀 Görüntülenme: {result['views']}")
        print(f"👍 Beğeni: {result['likes']}")
        print(f"👎 Beğenmeme: {result['dislikes']}")
    except Exception as e:
        print("❌ Hata:", e)

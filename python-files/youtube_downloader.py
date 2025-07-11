
from pytube import YouTube

def download_video():
    try:
        url = input("Вставьте ссылку на YouTube-видео: ").strip()
        yt = YouTube(url)
        stream = yt.streams.get_highest_resolution()
        print("Скачивание началось...")
        stream.download()
        print("Видео успешно скачано!")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    download_video()

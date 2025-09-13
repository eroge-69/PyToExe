import streamlink
import time
import os
from datetime import datetime
import subprocess


def convert_recording(input_path):
    base, ext = os.path.splitext(input_path)
    filename = os.path.basename(base)

    # Создаем папки если их нет
    video_dir = "video"
    audio_dir = "audio"
    os.makedirs(video_dir, exist_ok=True)
    os.makedirs(audio_dir, exist_ok=True)

    # Конвертация в MP4 (в папку video)
    mp4_path = os.path.join(video_dir, filename + ".mp4")
    subprocess.run(["ffmpeg", "-y", "-i", input_path, "-c", "copy", mp4_path])
    print(f"Создан видео файл: {mp4_path}")

    # Извлечение только аудио в MP3 (в папку audio)
    mp3_path = os.path.join(audio_dir, filename + ".mp3")
    subprocess.run(["ffmpeg", "-y", "-i", input_path, "-q:a", "0", "-map", "a", mp3_path])
    print(f"Создан аудио файл: {mp3_path}")

    return mp4_path, mp3_path

def is_twitch_stream_online(channel_name):
    """Проверяет, есть ли у стримера реальный поток"""
    try:
        session = streamlink.Streamlink()
        streams = session.streams(f"https://www.twitch.tv/{channel_name}")
        return "best" in streams
    except Exception:
        return False


def record_twitch_stream(channel_name, output_dir="recordings"):
    """Записывает Twitch стрим напрямую через streamlink"""
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{channel_name}_{timestamp}.ts"
    output_path = os.path.join(output_dir, filename)

    session = streamlink.Streamlink()
    streams = session.streams(f"https://www.twitch.tv/{channel_name}")

    if "best" not in streams:
        print("Нет доступных потоков (возможно, стример ещё не начал)")
        return None

    stream = streams["best"]
    fd = stream.open()
    print(f"Запись началась: {filename}")

    with open(output_path, "wb") as out_file:
        try:
            while True:
                data = fd.read(1024)
                if not data:
                    break
                out_file.write(data)
        except KeyboardInterrupt:
            print("Запись остановлена вручную")
        finally:
            fd.close()

    convert_recording(output_path)
    print("Запись завершена")
    return output_path


def main():
    channel = "5opka"  # ← замени на нужный канал
    check_interval = 30  # интервал проверки в секундах

    print(f"Мониторинг Twitch канала: {channel}")

    try:
        while True:
            if is_twitch_stream_online(channel):
                print("Стример онлайн! Начинаю запись...")
                record_twitch_stream(channel)
                print("Ожидаю следующего выхода в эфир...")
            else:
                print("Стример оффлайн. Проверяю через 30 секунд...")
                time.sleep(check_interval)
    except KeyboardInterrupt:
        print("\nМониторинг остановлен")


if __name__ == "__main__":
    main()


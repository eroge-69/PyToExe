import requests
import os
import time
from tqdm import tqdm

def animated_text(text, delay=0.1):
    """Печатает текст с анимацией печатания"""
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()

def download_dropbox_zip(dropbox_url, output_filename=None):
    """
    Скачивает файл по публичной ссылке Dropbox в папку, где лежит скрипт.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Превращаем ?dl=0 в ?dl=1, чтобы скачать файл напрямую
    url = dropbox_url
    if "dl=0" in url:
        url = url.replace("dl=0", "dl=1")

    if output_filename is None:
        output_filename = url.split("/")[-1].split("?")[0]

    file_path = os.path.join(script_dir, output_filename)

    # Запрос
    r = requests.get(url, stream=True)
    r.raise_for_status()

    total_size = int(r.headers.get("content-length", 0))
    block_size = 8192  # размер чанка

    animated_text("🚀 Подготовка к скачиванию...")
    time.sleep(0.5)

    with open(file_path, "wb") as f, tqdm(
        desc=f"⬇️  Скачиваю {output_filename}",
        total=total_size,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for chunk in r.iter_content(chunk_size=block_size):
            if chunk:
                f.write(chunk)
                bar.update(len(chunk))

    animated_text("✅ Загрузка завершена!")
    animated_text(f"Файл сохранён: {file_path}")

    return file_path


if __name__ == "__main__":
    dropbox_link = "https://www.dropbox.com/scl/fi/0867lzt9i5k25k9w8y58r/SpeedAutoClicker.zip?rlkey=qsf5yu35o752ngxtvqrsxfm1x&st=1bp3pgge&dl=0"

    animated_text("Добро пожаловать в загрузчик Dropbox 🎉")
    choice = input("Хотите скачать файл? (y/n): ").strip().lower()

    if choice == "y":
        download_dropbox_zip(dropbox_link)
    else:
        animated_text("❌ Загрузка отменена.")

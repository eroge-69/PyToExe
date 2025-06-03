import os
import ctypes
import urllib.request
import time
import sys

# Ссылка на ваше изображение (прямая загрузка через Dropbox)
IMAGE_URL = "https://www.dropbox.com/scl/fi/9x9i25sd1lmdh6dnkzpok/eblan.png?rlkey=n14uebu1a20gmaicj9hbkyjx8&st=p4y17v8v&dl=1"  # Обратите внимание на `dl=1` вместо `dl=0`

def set_wallpaper(url):
    try:
        # Скачиваем изображение во временную папку
        wallpaper_path = os.path.join(os.environ["TEMP"], "surprise_wallpaper.png")
        urllib.request.urlretrieve(url, wallpaper_path)
        
        # Устанавливаем обои (Windows)
        ctypes.windll.user32.SystemParametersInfoW(20, 0, wallpaper_path, 3)
        print("Z")
    except Exception as e:
        print("Z!")

def main():
    print("Z")
    time.sleep(2)
    
    # Меняем обои
    set_wallpaper(IMAGE_URL)
    
    # Можно добавить цикл для "неубиваемости"
    while True:
        print("Z")
        time.sleep(10)

if __name__ == "__main__":
    main()
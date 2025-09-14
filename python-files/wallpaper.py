import os
import ctypes

def set_wallpaper(path):
    # SPI_SETDESKWALLPAPER = 20
    ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 3)

if __name__ == "__main__":
    user_profile = os.environ['USERPROFILE']
    wallpaper_path = os.path.join(user_profile, 'Documents', 'wallpaper.png')
    if os.path.exists(wallpaper_path):
        set_wallpaper(wallpaper_path)
    else:
        print(f"Файл обоев не найден: {wallpaper_path}")

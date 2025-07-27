import os
import shutil
import time
import psutil
import threading
import winreg
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw
from plyer import notification

running = True
autolaunch_enabled = False
processed = set()
APP_NAME = "GModNodegraphWatcher"

# Создание иконки
def create_image():
    image = Image.new('RGB', (64, 64), color=(30, 144, 255))
    draw = ImageDraw.Draw(image)
    draw.rectangle((16, 28, 48, 36), fill=(255, 255, 255))
    return image

# Найти путь к GarrysMod (а не bin/win64)
def find_garrysmod_root():
    for proc in psutil.process_iter(['name', 'exe']):
        if proc.info['name'] == "gmod.exe":
            exe_path = proc.info['exe']
            if exe_path and os.path.exists(exe_path):
                # Удалим bin/win64 или bin
                garrysmod_root = exe_path
                for part in ["\\bin\\win64", "/bin/win64", "\\bin", "/bin"]:
                    if part in garrysmod_root.lower():
                        garrysmod_root = garrysmod_root.split(part)[0]
                return os.path.abspath(garrysmod_root)
    return None

# Уведомление
def notify(title, message):
    try:
        notification.notify(title=title, message=message, timeout=3)
    except:
        pass

# Добавить в автозагрузку Windows
def enable_autolaunch():
    exe_path = os.path.abspath(__file__).replace(".py", ".exe")
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, exe_path)
        winreg.CloseKey(key)
        return True
    except:
        return False

# Удалить из автозагрузки
def disable_autolaunch():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, APP_NAME)
        winreg.CloseKey(key)
        return True
    except:
        return False

# Проверить, включена ли автозагрузка
def is_autolaunch_enabled():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return True
    except:
        return False

# Мониторинг nodegraph
def monitor(icon):
    global running
    notify("GMod AIN Tracker", "Ожидание GMod...")

    gmod_path = None
    while running:
        gmod_path = find_garrysmod_root()
        if gmod_path:
            break
        time.sleep(1)

    notify("GMod AIN Tracker", f"GarrysMod найден:\n{gmod_path}")

    data_path = os.path.join(gmod_path, "garrysmod", "data", "nodegraph")
    output_path = os.path.join(gmod_path, "garrysmod", "maps", "graphs")
    os.makedirs(output_path, exist_ok=True)

    while running and find_garrysmod_root():
        if os.path.exists(data_path):
            for filename in os.listdir(data_path):
                if filename.endswith(".txt") and filename not in processed:
                    src = os.path.join(data_path, filename)
                    map_name = os.path.splitext(filename)[0]
                    dst = os.path.join(output_path, f"{map_name}.ain")

                    try:
                        shutil.copyfile(src, dst)
                        os.remove(src)
                        processed.add(filename)
                        notify("Nodegraph перенесён", f"{filename} → {map_name}.ain")
                    except Exception as e:
                        notify("Ошибка", str(e))
        time.sleep(1)

    notify("GMod AIN Tracker", "GMod закрыт.")
    icon.stop()

# Переключение автозапуска
def toggle_autolaunch(item):
    global autolaunch_enabled
    if autolaunch_enabled:
        disable_autolaunch()
        item.text = "Autolaunch OFF"
        autolaunch_enabled = False
        notify("Autolaunch", "Автозапуск отключен.")
    else:
        enable_autolaunch()
        item.text = "Autolaunch ON"
        autolaunch_enabled = True
        notify("Autolaunch", "Автозапуск включен.")

def quit_app(icon, item):
    global running
    running = False
    icon.stop()

# Главное меню
autolaunch_enabled = is_autolaunch_enabled()
menu = Menu(
    MenuItem("Autolaunch ON" if autolaunch_enabled else "Autolaunch OFF", toggle_autolaunch),
    MenuItem("Close", quit_app)
)

icon = Icon("GModAINTracker", icon=create_image(), menu=menu)
threading.Thread(target=monitor, args=(icon,), daemon=True).start()
icon.run()
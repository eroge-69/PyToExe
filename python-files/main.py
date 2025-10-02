import flet as ft
import os
import json
import glob
from pathlib import Path
import stat
import subprocess
import uuid
import hashlib
import requests
from datetime import datetime, timedelta
import base64
import pyperclip

TELEGRAM_BOT_TOKEN = "8428415535:AAFC9SuIifMAT4AJLNw8-d7hTwgeOwGli4w"
ADMIN_CHAT_ID = "8173298951"
settings_dir = Path.home() / "Documents" / "EulaTrap"
users_file = settings_dir / "users.json"
settings_file = settings_dir / "settings.json"

def encrypt_uid(uid):
    return base64.b64encode(uid.encode()).decode()

def decrypt_uid(encrypted_uid):
    return base64.b64decode(encrypted_uid.encode()).decode()

def save_user_uid(uid, ip_address):
    try:
        users = {}
        if users_file.exists():
            with open(users_file, "r", encoding="utf-8") as f:
                users = json.load(f)
        users[uid] = {"ip": ip_address, "chat_id": None}
        settings_dir.mkdir(parents=True, exist_ok=True)
        with open(users_file, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
    except Exception as ex:
        print(f"Error saving user UID: {ex}")

def send_to_telegram(uid, ip_address):
    try:
        message = f"🆕 Новая активация! 🎉\n📱 **UID**: `{uid}`\n🌐 **IP**: `{ip_address}`\n⏰ **Время**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": ADMIN_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, data=data, timeout=10)
        if response.status_code != 200:
            print(f"Telegram error (send_to_telegram): {response.text}")
    except Exception as ex:
        print(f"Telegram exception (send_to_telegram): {ex}")

def send_flags_to_telegram(uid, json_text):
    try:
        message_prefix = f"⚙️ Новые Fast Flags!\n📱 **UID**: `{uid}`\n⏰ **Время**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
       
        if len(json_text) > 3000:
            files = {'document': (f'flags_{uid}_{datetime.now().strftime("%H%M%S")}.json', json_text.encode('utf-8'), 'application/json')}
            data = {
                "chat_id": ADMIN_CHAT_ID,
                "caption": message_prefix,
                "parse_mode": "Markdown"
            }
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
            response = requests.post(url, data=data, files=files, timeout=10)
        else:
            message = f"{message_prefix}\n\n📄 **Flags**:\n```json\n{json_text}\n```"
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            data = {
                "chat_id": ADMIN_CHAT_ID,
                "text": message,
                "parse_mode": "Markdown"
            }
            response = requests.post(url, data=data, timeout=10)
       
        if response.status_code != 200:
            print(f"Telegram error (send_flags_to_telegram): {response.text}")
    except Exception as ex:
        print(f"Telegram exception (send_flags_to_telegram): {ex}")

def generate_uid():
    ip_address = get_ip_address()
    timestamp = str(datetime.now().timestamp())
    unique_string = f"{ip_address}_{timestamp}_{uuid.uuid4().hex}"
    uid = hashlib.md5(unique_string.encode()).hexdigest()[:8].upper()
    return uid, ip_address

def get_ip_address():
    try:
        response = requests.get('https://api.ipify.org', timeout=5)
        return response.text.strip()
    except:
        return "Unknown_IP_Error 🤷"

def check_first_run():
    return not settings_file.exists()

def save_settings(data):
    try:
        settings_dir.mkdir(parents=True, exist_ok=True)
        data_to_save = data.copy()
       
        if "uid" in data_to_save:
            data_to_save["encrypted_uid"] = encrypt_uid(data_to_save["uid"])
            del data_to_save["uid"]
        with open(settings_file, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)
    except Exception as ex:
        print(f"Error saving settings: {ex}")

def load_settings():
    try:
        if settings_file.exists():
            with open(settings_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "encrypted_uid" in data:
                data["uid"] = decrypt_uid(data["encrypted_uid"])
            return data
    except Exception as ex:
        print(f"Error loading settings: {ex}")
    return {}

def is_license_expired(settings):
    if settings.get("activated") and "activation_time" in settings:
        try:
            activation_time = datetime.fromisoformat(settings["activation_time"])
            if datetime.now() - activation_time > timedelta(days=7):
                return True
        except (ValueError, TypeError):
            return True
    return False

def main(page: ft.Page):
    page.title = "EulaTrap"
    page.window.width = 1000
    page.window.height = 600
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.bgcolor = ft.Colors.BLACK
   
    is_first_run = check_first_run()
    current_ip = get_ip_address()
    settings = load_settings()
    expired = is_license_expired(settings)
    generate_new_uid = is_first_run or \
                       "uid" not in settings or \
                       settings.get("ip", "") != current_ip or \
                       expired
                      
    if generate_new_uid:
        uid, ip_address = generate_uid()
        license_accepted = settings.get("license_accepted", False)
        settings = {"uid": uid, "ip": current_ip, "activated": False, "license_accepted": license_accepted}
        save_settings(settings)
        save_user_uid(uid, current_ip)
        send_to_telegram(uid, current_ip)
    else:
        uid = settings["uid"]
        if expired:
            settings["activated"] = False
            save_settings(settings)
           
    current_uid = uid
    current_settings = settings

    text_area = ft.TextField(
        multiline=True,
        min_lines=8,
        max_lines=8,
        expand=True,
        hint_text="Введите Fast Flags в формате JSON 🎮 (например, {\"FFlagDebugGraphicsPreferD3D11\": \"True\"})",
        border_radius=10,
        text_style=ft.TextStyle(font_family="Roboto", size=12),
        border=ft.InputBorder.OUTLINE,
        border_color=ft.Colors.BLUE_300,
        focused_border_color="#0055FF",
        border_width=2,
        tooltip="Введите JSON, например: {\"FFlagDebugGraphicsPreferD3D11\": \"True\", \"DFIntTaskSchedulerTargetFps\": 240}",
        disabled=True
    )
   
    def show_snackbar(message, color):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message, size=12, color=ft.Colors.WHITE),
            bgcolor=color,
            duration=4000
        )
        page.snack_bar.open = True
        page.update()

    def get_client_settings_path():
        local_appdata = os.getenv("LOCALAPPDATA")
        if local_appdata:
            return Path(local_appdata) / "Roblox" / "ClientSettings"
        return None

    def save_flags(e):
        json_text = text_area.value.strip()
        if not json_text:
            show_snackbar("Ошибка: Введите JSON данные! 📝", ft.Colors.RED_700)
            return
           
        try:
            json.loads(json_text)
        except json.JSONDecodeError:
            show_snackbar("Ошибка: Неверный формат JSON! ❌", ft.Colors.RED_700)
            return
           
        client_settings_dir = get_client_settings_path()
        if not client_settings_dir:
            show_snackbar("Не удалось найти папку LOCALAPPDATA! 📂", ft.Colors.RED_700)
            return
        try:
            client_settings_dir.mkdir(parents=True, exist_ok=True)
        except Exception as ex:
            show_snackbar(f"Ошибка создания папки: {str(ex)} 📂", ft.Colors.RED_700)
            return
           
        file_path = client_settings_dir / "ClientAppSettings.json"
   
        try:
            if file_path.exists():
                file_path.chmod(stat.S_IWRITE)
           
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(json_text)
           
            file_path.chmod(stat.S_IREAD | stat.S_IRUSR)
           
            show_snackbar("Успех! Флаги сохранены. ✅", ft.Colors.GREEN_700)
            send_flags_to_telegram(current_uid, json_text)
        except Exception as ex:
            show_snackbar(f"Ошибка при сохранении файла: {str(ex)} 💥", ft.Colors.RED_700)
        page.update()

    def launch_bloxstrap(e):
        try:
            possible_paths = [
                Path.home() / "Desktop" / "Bloxstrap.exe",
                Path(os.getenv("PROGRAMFILES", "C:/Program Files")) / "Bloxstrap" / "Bloxstrap.exe",
                Path(os.getenv("LOCALAPPDATA", "")) / "Bloxstrap" / "Bloxstrap.exe",
                Path.home() / "Downloads" / "Bloxstrap.exe"
            ]
           
            bloxstrap_path = None
            for path in possible_paths:
                if path.exists():
                    bloxstrap_path = path
                    break
           
            if not bloxstrap_path:
                search_patterns = [
                    str(Path.home() / "Desktop" / "Bloxstrap*.exe"),
                    str(Path.home() / "Downloads" / "Bloxstrap*.exe")
                ]
                for pattern in search_patterns:
                    matches = glob.glob(pattern)
                    if matches:
                        bloxstrap_path = matches[0]
                        break
           
            if bloxstrap_path:
                subprocess.Popen([bloxstrap_path])
                show_snackbar("Bloxstrap запущен! 🚀", ft.Colors.GREEN_700)
            else:
                show_snackbar("Ошибка: Bloxstrap.exe не найден! Убедитесь, что он установлен. ❌", ft.Colors.RED_700)
        except Exception as ex:
            show_snackbar(f"Ошибка при запуске Bloxstrap: {str(ex)} 💥", ft.Colors.RED_700)
        page.update()

    def show_instructions(e):
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Инструкция 📝", size=16, weight=ft.FontWeight.BOLD),
            content=ft.Text(
                "1. Скачайте Bloxstrap с официального сайта 🌐\n"
                "2. Введите Fast Flags в поле ✍️\n"
                "3. Нажмите 'Сохранить' 💾\n"
                "4. Нажмите 'Запустить' для первого старта с флагами. "
                "Затем можно использовать обычный ярлык Bloxstrap 🚀",
                size=14
            ),
            actions=[ft.TextButton("Понятно", on_click=lambda e: page.close(dialog))],
            actions_alignment=ft.MainAxisAlignment.END
        )
        page.open(dialog)
   
    def load_existing():
        client_settings_file = get_client_settings_path() / "ClientAppSettings.json"
        if client_settings_file.exists():
            try:
                with open(client_settings_file, 'r', encoding='utf-8') as f:
                    text_area.value = f.read()
                show_snackbar("Загружены существующие флаги. 📂", ft.Colors.BLUE_700)
                page.update()
            except Exception as ex:
                show_snackbar(f"Не удалось прочитать существующие флаги: {ex}", ft.Colors.ORANGE_700)

    save_button = ft.ElevatedButton(
        content=ft.Row([ft.Icon(ft.Icons.SAVE, size=16), ft.Text("Сохранить")], alignment=ft.MainAxisAlignment.CENTER),
        on_click=save_flags,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), bgcolor="#0055FF", color=ft.Colors.WHITE, elevation=8),
        width=150, height=40, disabled=True, tooltip="Сохранить Fast Flags"
    )
    launch_button = ft.ElevatedButton(
        content=ft.Row([ft.Icon(ft.Icons.ROCKET_LAUNCH, size=16), ft.Text("Запустить")], alignment=ft.MainAxisAlignment.CENTER),
        on_click=launch_bloxstrap,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE, elevation=8),
        width=150, height=40, disabled=True, tooltip="Запустить Bloxstrap"
    )
    instruction_button = ft.ElevatedButton(
        content=ft.Row([ft.Icon(ft.Icons.BOOK, size=16), ft.Text("Инструкция")], alignment=ft.MainAxisAlignment.CENTER),
        on_click=show_instructions,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), bgcolor=ft.Colors.GREY_700, color=ft.Colors.WHITE, elevation=8),
        width=150, height=40, disabled=False, tooltip="Показать инструкцию"
    )
   
    def enable_main_ui(is_enabled: bool):
        text_area.disabled = not is_enabled
        save_button.disabled = not is_enabled
        launch_button.disabled = not is_enabled
        page.update()

    def copy_uid(e):
        pyperclip.copy(current_uid)
        show_snackbar("UID скопирован в буфер обмена! 📋", ft.Colors.GREEN_700)

    def activate_uid(e):
        entered_uid = uid_input.value.strip().upper()
        if entered_uid == current_uid:
            current_settings["activated"] = True
            current_settings["activation_time"] = datetime.now().isoformat()
            save_settings(current_settings)
            show_snackbar("✅ UID активирован! Добро пожаловать! 🎉", ft.Colors.GREEN_700)
           
            activation_view.visible = False
            main_view.visible = True
            enable_main_ui(True)
            load_existing()
            page.update()
        else:
            show_snackbar("❌ Неверный UID! Проверьте правильность ввода. 🛑", ft.Colors.RED_700)
            uid_input.value = ""
            page.update()

    def accept_license(e):
        current_settings["license_accepted"] = True
        save_settings(current_settings)
   
        license_view.visible = False
        if not current_settings.get("activated", False) or expired:
            activation_view.visible = True
            show_snackbar(f"🎉 Соглашение принято! Теперь активируйте ваш UID.", ft.Colors.BLUE_700)
        else:
            main_view.visible = True
            enable_main_ui(True)
            show_snackbar("✅ Добро пожаловать обратно! 👋", ft.Colors.GREEN_700)
            load_existing()
        page.update()

    def close_app(e):
        page.window.destroy()

    uid_input = ft.TextField(
        label="UID для активации",
        border_radius=10,
        text_style=ft.TextStyle(font_family="Roboto", size=12),
        border=ft.InputBorder.OUTLINE,
        border_color=ft.Colors.BLUE_300,
        focused_border_color="#0055FF",
        width=250,
        text_align=ft.TextAlign.CENTER
    )

    copy_button = ft.IconButton(
        icon=ft.Icons.COPY,
        on_click=copy_uid,
        tooltip="Копировать UID",
        icon_color=ft.Colors.WHITE
    )

    license_view = ft.Column(
        [
            ft.Text("Лицензионное соглашение 📜", size=24, weight=ft.FontWeight.BOLD),
            ft.Text(
                "Используя это приложение, вы соглашаетесь, что:\n"
                "• Мы не несём ответственность за возможные баны, удаление аккаунта или другие последствия, связанные с использованием Fast Flags в Roblox.\n"
                "• Вы используете приложение на свой страх и риск. 🚨",
                size=14,
                color=ft.Colors.WHITE70
            ),
            ft.Row(
                [
                    ft.ElevatedButton("Выйти", on_click=close_app, bgcolor=ft.Colors.RED_700),
                    ft.ElevatedButton("Я согласен", on_click=accept_license, bgcolor=ft.Colors.GREEN_700),
                ],
                alignment=ft.MainAxisAlignment.END
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20,
        expand=True,
        visible=False
    )
   
    activation_view = ft.Column(
        [
            ft.Text("Активация программы 🔑", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("Для продолжения, пожалуйста, активируйте вашу копию.", color=ft.Colors.WHITE70),
            ft.Row(
                [
                    ft.Text("Ваш UID: ", size=16),
                    ft.Text(current_uid, size=16, weight=ft.FontWeight.BOLD, selectable=True, color=ft.Colors.GREEN_400),
                    copy_button
                ],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            ft.Row(
                [uid_input],
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True
            ),
            ft.Row(
                [ft.ElevatedButton("Активировать", icon=ft.Icons.VERIFIED, on_click=activate_uid, bgcolor="#FFD700", color=ft.Colors.BLACK)],
                alignment=ft.MainAxisAlignment.CENTER
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20,
        expand=True,
        visible=False
    )

    main_view = ft.Column(
        [
            ft.Row(
                [
                    ft.Icon(ft.Icons.FLAG_CIRCLE, color="#0055FF", size=32),
                    ft.Text("EulaTrap Fast Flag Editor", size=24, weight=ft.FontWeight.BOLD)
                ],
                spacing=10
            ),
            ft.Text("Вставьте ваш JSON с флагами ниже.", color=ft.Colors.WHITE70),
            text_area,
            ft.Row(
                [save_button, launch_button, instruction_button],
                alignment=ft.MainAxisAlignment.SPACE_AROUND
            )
        ],
        spacing=15,
        visible=False
    )
    page.add(license_view, activation_view, main_view)
    if not current_settings.get("license_accepted", False):
        license_view.visible = True
    elif not current_settings.get("activated", False) or expired:
        activation_view.visible = True
    else:
        main_view.visible = True
        enable_main_ui(True)
        load_existing()
   
    page.update()

if __name__ == "__main__":
    ft.app(target=main)
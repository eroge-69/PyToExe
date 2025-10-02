import customtkinter as ctk
import winreg
import os
import subprocess
import threading
from pathlib import Path
import shutil
import json
import logging
import minecraft_launcher_lib
import platform
import re
import requests
import zipfile
import io

# Настройка логирования
logging.basicConfig(filename='launcher.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class TotalWarLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Project Total War: Launcher")
        self.root.geometry("400x400")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.frame = ctk.CTkFrame(master=self.root)
        self.frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.label_nickname = ctk.CTkLabel(master=self.frame, text="Nickname:")
        self.label_nickname.pack(pady=10)
        self.entry_nickname = ctk.CTkEntry(master=self.frame, placeholder_text="Enter your nickname")
        self.entry_nickname.pack(pady=5)

        self.label_register = ctk.CTkLabel(master=self.frame, text="Registration Code:")
        self.label_register.pack(pady=10)
        self.entry_register = ctk.CTkEntry(master=self.frame, placeholder_text="Enter registration code")
        self.entry_register.pack(pady=5)

        self.label_memory = ctk.CTkLabel(master=self.frame, text="RAM (GB): 2")
        self.label_memory.pack(pady=10)
        self.slider_memory = ctk.CTkSlider(master=self.frame, from_=2, to=8, number_of_steps=6, command=self.update_memory_label)
        self.slider_memory.set(4)
        self.slider_memory.pack(pady=10)

        self.button_action = ctk.CTkButton(master=self.frame, text="Установить", command=self.button_action_click)
        self.button_action.pack(pady=20)
        self.button_action.configure(state="disabled")

        self.status_label = ctk.CTkLabel(master=self.frame, text="")
        self.status_label.pack(pady=10)

        self.client_dir = Path(r"C:\PTW\Client")
        self.versions_dir = self.client_dir / "versions"
        self.vanilla_version = "1.20.1"
        self.forge_version = minecraft_launcher_lib.forge.find_forge_version(self.vanilla_version)
        self.installed = False
        self.mods_dir = self.client_dir / "mods"
        self.libraries_dir = self.client_dir / "libraries"

        self.mods_url = "https://www.dropbox.com/scl/fi/c1vnnv0i6lkejsxsgukil/PTW.s.zip?rlkey=0ejwc7wals169btxt3oo7wunc&st=x85y734n&dl=1"
        self.libraries_url = "https://www.dropbox.com/scl/fi/jgyfxfx3l952l3vwmaxhx/libraries.zip?rlkey=qvilljeq9cv2awu4mq6jx1eoe&st=g2c1kmtr&dl=1"

        self.required_mods = [
            "voicechat-forge-1.20.1-2.6.4.jar"
        ]

        self.registration_server_url = "http://your-registration-server.com/register" # Replace with your actual server URL

        self.load_settings()

        threading.Thread(target=self.initial_check, daemon=True).start()

    def initial_check(self):
        if self.check_installation():
            self.installed = True
            self.button_action.configure(text="Запустить", state="normal")
            self.update_status("Все файлы на месте", "green")
        else:
            self.button_action.configure(text="Установить", state="normal")
            self.update_status("Требуется установка", "yellow")

    def check_java(self):
        try:
            result = subprocess.run(['java', '-version'], capture_output=True, text=True)
            version_info = result.stderr
            version = float(re.search(r'version "(\d+\.\d+)', version_info).group(1))
            return version >= 17.0
        except (subprocess.CalledProcessError, FileNotFoundError, AttributeError):
            logging.error("Java 17+ not found")
            return False

    def update_memory_label(self, value):
        self.label_memory.configure(text=f"RAM (GB): {int(value)}")

    def update_status(self, message, color="white"):
        self.status_label.configure(text=message, text_color=color)
        self.root.update()

    def load_settings(self):
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\TotalWarLauncher") as key:
                nickname, _ = winreg.QueryValueEx(key, "Nickname")
                memory, _ = winreg.QueryValueEx(key, "Memory")
                if nickname:
                    self.entry_nickname.delete(0, ctk.END)
                    self.entry_nickname.insert(0, nickname)
                if memory:
                    memory = int(memory)
                    if 2 <= memory <= 8:  # Ensure memory is within slider range
                        self.slider_memory.set(memory)
                        self.update_memory_label(memory)
                logging.info("Settings loaded from registry")
        except FileNotFoundError:
            logging.info("No previous settings found in registry")
        except Exception as e:
            logging.error(f"Failed to load settings from registry: {e}")
            self.update_status("Ошибка загрузки настроек", "red")

    def save_settings(self):
        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\TotalWarLauncher")
            nickname = self.entry_nickname.get().strip()
            if not nickname:
                nickname = "Player"
            winreg.SetValueEx(key, "Nickname", 0, winreg.REG_SZ, nickname)
            memory = int(self.slider_memory.get())
            winreg.SetValueEx(key, "Memory", 0, winreg.REG_DWORD, memory)
            winreg.CloseKey(key)
            logging.info(f"Settings saved to registry: Nickname={nickname}, Memory={memory}G")
        except Exception as e:
            logging.error(f"Failed to save settings to registry: {e}")
            self.update_status("Ошибка сохранения настроек", "red")

    def check_installation(self):
        try:
            version_path = self.versions_dir / self.forge_version
            json_path = version_path / f"{self.forge_version}.json"
            if not (version_path.exists() and json_path.exists()):
                logging.info("Forge version or JSON file missing")
                return False

            if not self.mods_dir.exists():
                logging.info("Mods directory missing")
                return False

            for mod in self.required_mods:
                mod_path = self.mods_dir / mod
                if not mod_path.exists():
                    logging.info(f"Required mod missing: {mod}")
                    return False

            if not self.libraries_dir.exists():
                logging.info("Libraries directory missing")
                return False

            assets_dir = self.client_dir / "assets"
            if not assets_dir.exists():
                logging.info("Assets directory missing")
                return False

            return True
        except Exception as e:
            logging.error(f"Error checking installation: {e}")
            return False

    def download_and_extract_mods(self):
        try:
            self.update_status("Скачивание модов...")
            response = requests.get(self.mods_url, stream=True)
            if response.status_code != 200:
                raise Exception(f"Failed to download mods: HTTP {response.status_code}")

            self.update_status("Распаковка модов...")
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                ptw_s_folder = None
                for item in z.namelist():
                    if item.startswith("PTW.s/"):
                        ptw_s_folder = "PTW.s"
                        break

                if not ptw_s_folder:
                    raise Exception("PTW.s folder not found in archive")

                for item in z.namelist():
                    if item.startswith(f"{ptw_s_folder}/"):
                        relative_path = item[len(f"{ptw_s_folder}/"):]
                        if not relative_path:
                            continue
                        target_path = self.client_dir / relative_path
                        if item.endswith('/'):
                            target_path.mkdir(parents=True, exist_ok=True)
                        else:
                            with z.open(item) as source, open(target_path, "wb") as target:
                                shutil.copyfileobj(source, target)

            self.update_status("Моды установлены", "green")
            return True
        except Exception as e:
            logging.error(f"Failed to download or extract mods: {e}")
            self.update_status(f"Ошибка при установке модов: {e}", "red")
            return False

    def download_and_extract_libraries(self):
        try:
            self.update_status("Скачивание библиотек...")
            response = requests.get(self.libraries_url, stream=True)
            if response.status_code != 200:
                raise Exception(f"Failed to download libraries: HTTP {response.status_code}")

            if self.libraries_dir.exists():
                self.update_status("Удаление старой папки библиотек...")
                shutil.rmtree(self.libraries_dir)

            self.update_status("Распаковка библиотек...")
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                z.extractall(self.client_dir)

            self.update_status("Библиотеки установлены", "green")
            return True
        except Exception as e:
            logging.error(f"Failed to download or extract libraries: {e}")
            self.update_status(f"Ошибка при установке библиотек: {e}", "red")
            return False

    def install_forge(self):
        try:
            self.update_status("Установка Forge...")
            minecraft_launcher_lib.forge.install_forge_version(
                self.forge_version,
                self.client_dir,
                callback={
                    "setStatus": lambda text: self.update_status(text),
                    "setProgress": lambda value: None,
                    "setMax": lambda value: None
                }
            )
            self.update_status("Forge установлен", "green")

            if not self.download_and_extract_libraries():
                return False

            return True
        except Exception as e:
            logging.error(f"Failed to install Forge: {e}")
            self.update_status(f"Ошибка при установке Forge: {e}", "red")
            return False

    def register_user(self):
        nickname = self.entry_nickname.get().strip()
        reg_code = self.entry_register.get().strip()

        if not nickname or not reg_code:
            self.update_status("Пожалуйста, введите никнейм и код регистрации.", "red")
            return False

        try:
            payload = {
                "username": nickname,
                "registration_code": reg_code
            }
            response = requests.post(self.registration_server_url, json=payload)

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.update_status("Регистрация успешна!", "green")
                    logging.info(f"User registered successfully: {nickname}")
                    return True
                else:
                    error_message = data.get("message", "Неизвестная ошибка регистрации.")
                    self.update_status(f"Ошибка регистрации: {error_message}", "red")
                    logging.warning(f"Registration failed for {nickname}: {error_message}")
                    return False
            else:
                self.update_status(f"Ошибка сервера регистрации: {response.status_code}", "red")
                logging.error(f"Registration server error: {response.status_code} - {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            self.update_status(f"Ошибка соединения с сервером регистрации: {e}", "red")
            logging.error(f"Error connecting to registration server: {e}")
            return False
        except Exception as e:
            self.update_status(f"Неожиданная ошибка при регистрации: {e}", "red")
            logging.error(f"Unexpected error during registration: {e}")
            return False


    def launch_forge(self):
        nickname = self.entry_nickname.get()
        if not nickname:
            self.update_status("Введите никнейм", "red")
            return

        memory = int(self.slider_memory.get())
        options = {
            "username": nickname,
            "uuid": "0",
            "token": "",
            "jvmArguments": [f"-Xmx{memory}G", f"-Xms{memory}G"],
            "launcherName": "TotalWarLauncher",
            "launcherVersion": "1.0",
            "gameDirectory": str(self.client_dir)
        }

        try:
            forge_version_string = f"{self.vanilla_version}-forge-{minecraft_launcher_lib.forge.get_forge_version_from_installer(self.forge_version)}"

            minecraft_command = minecraft_launcher_lib.command.get_minecraft_command(
                version=forge_version_string,
                minecraft_directory=str(self.client_dir),
                options=options
            )

            if not minecraft_command:
                raise ValueError("Failed to generate Minecraft command")

            logging.debug(f"Minecraft command: {minecraft_command}")

            subprocess.run(
                minecraft_command,
                cwd=str(self.client_dir),
                check=True
            )
            self.update_status("Minecraft запущен", "green")
        except Exception as e:
            logging.error(f"Failed to launch Forge: {e}")
            self.update_status(f"Ошибка при запуске: {e}", "red")

    def button_action_click(self):
        threading.Thread(target=self.perform_action, daemon=True).start()

    def perform_action(self):
        self.button_action.configure(state="disabled")
        self.save_settings()

        if not self.installed:
            if not self.register_user(): # Perform registration first
                self.button_action.configure(state="normal")
                return

            self.client_dir.mkdir(parents=True, exist_ok=True)
            self.versions_dir.mkdir(exist_ok=True)
            self.mods_dir.mkdir(exist_ok=True)
            self.libraries_dir.mkdir(exist_ok=True)

            if self.install_forge() and self.download_and_extract_mods():
                self.installed = True
                self.button_action.configure(text="Запустить")
                self.update_status("Установка завершена", "green")
        else:
            self.launch_forge()

        self.button_action.configure(state="normal")

if __name__ == "__main__":
    root = ctk.CTk()
    app = TotalWarLauncher(root)
    root.mainloop()


self.label_register = ctk.CTkLabel(master=self.frame, text="Registration Code:")
self.entry_register = ctk.CTkEntry(master=self.frame, placeholder_text="Enter registration code")


self.registration_server_url = "http://213.152.43.100:25742/register"



app = Flask(__name__)

# Список действительных кодов регистрации (в реальном приложении это будет база данных)
valid_registration_codes = {
    "CODE123",
    "PTW456",
    "LAUNCHER789"
}

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    registration_code = data.get('registration_code')

    if not username or not registration_code:
        return jsonify({"success": False, "message": "Missing username or registration code"}), 400

    if registration_code in valid_registration_codes:
        # выдали ему уникальный токен и т.д.
        print(f"User '{username}' registered successfully with code '{registration_code}'")
        return jsonify({"success": True, "message": "Registration successful!"}), 200
    else:
        print(f"Failed registration for '{username}': Invalid code '{registration_code}'")
        return jsonify({"success": False, "message": "Invalid registration code"}), 200

if __name__ == '__main__':
    # Запустите сервер на порту 5000 (или другом)
    # Для доступности извне, вам может потребоваться настроить проброс портов или использовать ngrok.
    app.run(debug=True, port=5000)
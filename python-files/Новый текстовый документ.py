import os
import ctypes
import tempfile
import requests
import subprocess
import shutil
from tkinter import filedialog, Tk
import tkinter.messagebox as messagebox
from pathlib import Path

class XashHelper:
    def __init__(self):
        self.install_dir = ""
        self.urls = {
            "valve_files": "https://github.com/ch3ryyy/HLAndCSFilesForXash3d/releases/download/half-life/valve.rar",
            "cstrike_files": "https://github.com/ch3ryyy/HLAndCSFilesForXash3d/releases/download/counter-strike/cstrike.rar",
            "xash": "https://github.com/FWGS/xash3d-fwgs/releases/download/continuous/xash3d-fwgs-win32-i386.7z",
            "cs_client": "https://github.com/Velaron/cs16-client/releases/download/continuous/CS16Client-Windows-X86.zip",
            "7zip": "https://www.7-zip.org/a/7z2301-x64.exe",
            "vc_redist": "https://aka.ms/vs/17/release/vc_redist.x86.exe"
        }

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def select_folder(self):
        root = Tk()
        root.withdraw()
        folder = filedialog.askdirectory(title="Выберите папку для Xash3D")
        root.destroy()
        
        if not folder:
            return False
        
        try:
            Path(folder).mkdir(parents=True, exist_ok=True)
            self.install_dir = folder
            return True
        except Exception as e:
            print(f"Ошибка: {e}")
            return False

    def download_file(self, url, filename):
        try:
            temp_file = os.path.join(tempfile.gettempdir(), filename)
            print(f"Скачивание {filename}...")
            
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            block_size = 8192
            
            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=block_size):
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    percent = downloaded_size / total_size * 100 if total_size > 0 else 0
                    print(f"\rПрогресс: {percent:.1f}%", end="", flush=True)
            
            print()
            return temp_file
        except Exception as e:
            print(f"Ошибка: {e}")
            return None

    def install_dependencies(self):
        try:
            vc_redist_installed = False
            try:
                result = subprocess.run(["where", "vcredist_x86.exe"], capture_output=True, text=True)
                vc_redist_installed = result.returncode == 0
            except:
                pass
                
            if not vc_redist_installed:
                vc_redist_file = self.download_file(self.urls['vc_redist'], 'vc_redist.x86.exe')
                if vc_redist_file:
                    subprocess.run([vc_redist_file, "/quiet", "/norestart"], check=True)
                    os.remove(vc_redist_file)

            seven_zip_installed = False
            possible_paths = [
                os.path.join(os.environ['ProgramFiles'], '7-Zip', '7z.exe'),
                os.path.join(os.environ['ProgramFiles(x86)'], '7-Zip', '7z.exe'),
                '7z.exe'
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    seven_zip_installed = True
                    break
            
            if not seven_zip_installed:
                seven_zip_file = self.download_file(self.urls['7zip'], '7zsetup.exe')
                if seven_zip_file:
                    subprocess.run([seven_zip_file, '/S'], check=True)
                    os.remove(seven_zip_file)
        except Exception as e:
            print(f"Ошибка: {e}")

    def extract_archive(self, archive_path, destination):
        try:
            seven_zip_path = None
            possible_paths = [
                os.path.join(os.environ['ProgramFiles'], '7-Zip', '7z.exe'),
                os.path.join(os.environ['ProgramFiles(x86)'], '7-Zip', '7z.exe'),
                '7z.exe'
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    seven_zip_path = path
                    break
            
            if not seven_zip_path:
                return False
            
            subprocess.run(
                [seven_zip_path, 'x', '-y', f'-o{destination}', archive_path],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            return True
        except Exception:
            return False

    def install_xash(self):
        temp_file = self.download_file(self.urls['xash'], 'xash3d.7z')
        if not temp_file:
            return False
        
        success = self.extract_archive(temp_file, self.install_dir)
        os.remove(temp_file)
        return success

    def install_cs(self):
        temp_file = self.download_file(self.urls['cs_client'], 'cs16.zip')
        if not temp_file:
            return False
        
        success = self.extract_archive(temp_file, self.install_dir)
        os.remove(temp_file)
        return success

    def install_valve(self):
        temp_file = self.download_file(self.urls['valve_files'], 'valve.rar')
        if not temp_file:
            return False
        
        success = self.extract_archive(temp_file, self.install_dir)
        os.remove(temp_file)
        return success

    def install_cstrike(self):
        temp_file = self.download_file(self.urls['cstrike_files'], 'cstrike.rar')
        if not temp_file:
            return False
        
        success = self.extract_archive(temp_file, self.install_dir)
        os.remove(temp_file)
        return success

    def create_shortcut(self, target, name, arguments="", icon_path=None):
        try:
            from win32com.client import Dispatch
            desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
            shortcut_path = os.path.join(desktop, f"{name}.lnk")
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.TargetPath = target
            shortcut.Arguments = arguments
            shortcut.WorkingDirectory = os.path.dirname(target)
            
            if icon_path and os.path.exists(icon_path):
                shortcut.IconLocation = icon_path
            
            shortcut.save()
            return True
        except Exception:
            return False

    def create_shortcuts(self):
        if not self.install_dir:
            return False
        
        xash_path = os.path.join(self.install_dir, 'xash3d.exe')
        if not os.path.exists(xash_path):
            return False
        
        self.create_shortcut(xash_path, "Xash3D")
        
        cstrike_path = os.path.join(self.install_dir, 'cstrike')
        if os.path.exists(cstrike_path):
            icon_path = os.path.join(cstrike_path, 'game.ico') if os.path.exists(os.path.join(cstrike_path, 'game.ico')) else None
            self.create_shortcut(
                xash_path,
                "CS 1.6 (Xash3D)",
                arguments="-game cstrike",
                icon_path=icon_path
            )
        
        return True

    def run(self):
        if not self.select_folder():
            return
        
        self.install_dependencies()
        
        while True:
            self.clear_screen()
            print("=========================")
            print(" Универсальный помощник Xash3D")
            print("=========================")
            print(f"\nПапка: {self.install_dir}\n")
            print("1. Установить Xash3D")
            print("2. Установить CS 1.6")
            print("3. Установить файлы Half-Life")
            print("4. Установить файлы CS 1.6")
            print("5. Создать ярлыки")
            print("6. Сменить папку")
            print("0. Выход\n")
            
            choice = input("Выбор: ")
            
            if choice == "0":
                break
            elif choice == "1":
                self.install_xash()
            elif choice == "2":
                self.install_cs()
            elif choice == "3":
                self.install_valve()
            elif choice == "4":
                self.install_cstrike()
            elif choice == "5":
                self.create_shortcuts()
            elif choice == "6":
                self.select_folder()
            
            input()

if __name__ == "__main__":
    helper = XashHelper()
    helper.run()
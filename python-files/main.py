import os
import tempfile
import shutil
import platform
import string
import random
from datetime import datetime, timedelta

class LicenseManager:
    @staticmethod
    def generate_license_key(length=20):
        chars = string.ascii_uppercase + string.digits
        key = ''.join(random.choice(chars) for _ in range(length))
        parts = [key[i:i+5] for i in range(0, length, 5)]
        return '-'.join(parts)

    @staticmethod
    def encode_license(license_key, issue_date):
        return f"{license_key}|{issue_date.strftime('%Y%m%d')}"

    @staticmethod
    def decode_license(license_str):
        try:
            key, date_str = license_str.split('|')
            issue_date = datetime.strptime(date_str, '%Y%m%d')
            return key, issue_date
        except Exception:
            return None, None

    @staticmethod
    def verify_license_key(license_str):
        key, issue_date = LicenseManager.decode_license(license_str)
        if not key or not issue_date:
            return False
        parts = key.split('-')
        if len(parts) != 4:
            return False
        for part in parts:
            if len(part) != 5 or not part.isalnum() or not part.isupper():
                return False
        now = datetime.now()
        if now > issue_date + timedelta(days=365):
            return False
        return True

class Cleaner:
    def __init__(self):
        self.temp_dirs = [
            tempfile.gettempdir(),
            os.path.expandvars(r'%TEMP%') if platform.system() == "Windows" else None,
            os.path.expanduser('~/.cache') if platform.system() != "Windows" else None,
        ]

    def clear_temp_files(self):
        print("Suppression des fichiers temporaires...")
        for temp_dir in self.temp_dirs:
            if temp_dir and os.path.exists(temp_dir):
                self._delete_files_in_dir(temp_dir)

    def _delete_files_in_dir(self, directory):
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                    except Exception:
                        pass
                for dir_ in dirs:
                    dir_path = os.path.join(root, dir_)
                    try:
                        shutil.rmtree(dir_path)
                    except Exception:
                        pass
        except Exception as e:
            print(f"Erreur lors de la suppression dans {directory}: {e}")

    def clear_recycle_bin(self):
        if platform.system() == "Windows":
            print("Vidage de la corbeille...")
            try:
                import ctypes
                result = ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0x0007)
                if result == 0:
                    print("Corbeille vidée avec succès.")
                else:
                    print("Erreur lors du vidage de la corbeille.")
            except Exception as e:
                print(f"Impossible de vider la corbeille: {e}")
        else:
            print("Vidage de la corbeille non supporté sur ce système.")

    def clean_browser_cache(self):
        print("Nettoyage du cache des navigateurs (Chrome et Firefox)...")
        user_home = os.path.expanduser("~")
        # Chrome
        chrome_cache = None
        if platform.system() == "Windows":
            chrome_cache = os.path.join(user_home, "AppData", "Local", "Google", "Chrome", "User Data", "Default", "Cache")
        elif platform.system() == "Linux":
            chrome_cache = os.path.join(user_home, ".cache", "google-chrome", "Default", "Cache")
        if chrome_cache and os.path.exists(chrome_cache):
            self._delete_files_in_dir(chrome_cache)

        # Firefox
        firefox_cache = None
        if platform.system() == "Windows":
            firefox_cache = os.path.join(user_home, "AppData", "Local", "Mozilla", "Firefox", "Profiles")
        elif platform.system() == "Linux":
            firefox_cache = os.path.join(user_home, ".cache", "mozilla", "firefox")
        if firefox_cache and os.path.exists(firefox_cache):
            for profile in os.listdir(firefox_cache):
                cache_path = os.path.join(firefox_cache, profile, "cache2")
                if os.path.exists(cache_path):
                    self._delete_files_in_dir(cache_path)

    def full_cleanup(self):
        self.clear_temp_files()
        self.clear_recycle_bin()
        self.clean_browser_cache()
        print("Nettoyage complet effectué.")

def main():
    license_file = "license.key"
    try:
        with open(license_file, "r") as f:
            license_str = f.read().strip()
    except FileNotFoundError:
        key = LicenseManager.generate_license_key()
        issue_date = datetime.now()
        license_str = LicenseManager.encode_license(key, issue_date)
        with open(license_file, "w") as f:
            f.write(license_str)
        print(f"Nouvelle clé de licence générée (valable 1 an): {license_str}")

    if not LicenseManager.verify_license_key(license_str):
        print("Clé de licence invalide ou expirée. Fin du programme.")
        return

    print("Clé de licence valide. Lancement du nettoyeur...")

    cleaner = Cleaner()
    cleaner.full_cleanup()
    print("Nettoyage terminé.")

if __name__ == "__main__":
    main()
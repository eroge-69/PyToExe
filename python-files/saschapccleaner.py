import os
import sys
import shutil
import json
import tempfile
import random
import string

class PCCleaner:
    def __init__(self):
        self.keys_file = "keys.json"
        self.config_file = "config.json"
        self.admin_password = "admin123"
        self.valid_keys = self.load_keys()
        
        # Füge Standard-Key für diesen PC hinzu
        self.master_key = "SS-444-555-666"
        if self.master_key not in self.valid_keys:
            self.valid_keys[self.master_key] = True
            self.save_keys()
            
        self.activated = False
        
    def load_keys(self):
        if os.path.exists(self.keys_file):
            try:
                with open(self.keys_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_keys(self):
        with open(self.keys_file, 'w') as f:
            json.dump(self.valid_keys, f, indent=4)

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_header(self):
        print("=" * 50)
        print("           PC CLEANER TOOL")
        print("=" * 50)
        print(f"Status: {'Aktiviert' if self.activated else 'Nicht aktiviert'}")
        print("=" * 50)
    
    def display_menu(self):
        print("[01] Clear Recycle Bin")
        print("[02] Clear Temp folder")
        print("[03] Clear Prefetch")
        print("[04] Clear Browser Cache")
        print("[05] Clear Downloads")
        print("[06] Clear Recent Files")
        print("[07] Clear Clipboard")
        print("[08] Clear System Logs")
        print("[09] Clear Temporary Internet Files")
        print("[10] Clear Windows Update Cache")
        print("[11] Clear Error Reports")
        print("[12] Clear Thumbnail Cache")
        print("[13] Flush DNS Cache")
        print("[14] Clear Font Cache")
        print("[15] Clear AppData Temp")
        print("[16] Clear Windows Temp")
        print("[17] Clear User Temp")
        print("[18] Clear Crash Dumps")
        print("[19] Clear Memory Dumps")
        print("[20] Clear Delivery Optimization Cache")
        print("[21] Admin-Menü (Passwort: admin123)")
        print("[22] EXIT")
        print("=" * 50)

    def clear_recycle_bin(self):
        try:
            if os.name == 'nt':
                os.system('rd /s /q C:\\$Recycle.bin 2>nul')
            print("✅ Papierkorb wurde geleert.")
        except Exception as e:
            print(f"❌ Fehler beim Leeren des Papierkorbs: {e}")

    def clear_temp_folder(self):
        try:
            temp_dir = tempfile.gettempdir()
            for item in os.listdir(temp_dir):
                item_path = os.path.join(temp_dir, item)
                try:
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                except:
                    pass
            print("✅ Temp-Ordner wurde geleert.")
        except Exception as e:
            print(f"❌ Fehler beim Leeren des Temp-Ordners: {e}")

    def clear_prefetch(self):
        try:
            prefetch_path = os.path.join(os.environ.get('SYSTEMROOT', 'C:\\Windows'), 'Prefetch')
            if os.path.exists(prefetch_path):
                for file in os.listdir(prefetch_path):
                    try:
                        file_path = os.path.join(prefetch_path, file)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                    except:
                        pass
                print("✅ Prefetch wurde geleert.")
            else:
                print("❌ Prefetch-Ordner nicht gefunden.")
        except Exception as e:
            print(f"❌ Fehler beim Leeren des Prefetch: {e}")

    def clear_browser_cache(self):
        try:
            # Chrome Cache
            chrome_path = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google', 'Chrome', 'User Data', 'Default', 'Cache')
            if os.path.exists(chrome_path):
                shutil.rmtree(chrome_path, ignore_errors=True)
            
            # Firefox Cache
            firefox_path = os.path.join(os.environ.get('APPDATA', ''), 'Mozilla', 'Firefox', 'Profiles')
            if os.path.exists(firefox_path):
                for profile in os.listdir(firefox_path):
                    cache_path = os.path.join(firefox_path, profile, 'cache2')
                    if os.path.exists(cache_path):
                        shutil.rmtree(cache_path, ignore_errors=True)
            
            print("✅ Browser-Cache wurde geleert.")
        except Exception as e:
            print(f"❌ Fehler beim Leeren des Browser-Caches: {e}")

    def clear_downloads(self):
        try:
            downloads_path = os.path.join(os.environ.get('USERPROFILE', ''), 'Downloads')
            if os.path.exists(downloads_path):
                for item in os.listdir(downloads_path):
                    item_path = os.path.join(downloads_path, item)
                    try:
                        if os.path.isfile(item_path):
                            os.remove(item_path)
                        elif os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                    except:
                        pass
                print("✅ Downloads-Ordner wurde geleert.")
        except Exception as e:
            print(f"❌ Fehler beim Leeren des Downloads-Ordners: {e}")

    def clear_clipboard(self):
        try:
            if os.name == 'nt':
                os.system('echo off | clip')
            print("✅ Zwischenablage wurde geleert.")
        except Exception as e:
            print(f"❌ Fehler beim Leeren der Zwischenablage: {e}")

    def flush_dns(self):
        try:
            if os.name == 'nt':
                os.system('ipconfig /flushdns')
                print("✅ DNS-Cache wurde geleert.")
        except Exception as e:
            print(f"❌ Fehler beim Leeren des DNS-Cache: {e}")

    def generate_key(self):
        """Erstellt einen neuen Key im Format SS-XXX-XXX-XXX"""
        key = 'SS-' + ''.join(random.choices(string.digits, k=3)) + '-' + ''.join(random.choices(string.digits, k=3)) + '-' + ''.join(random.choices(string.digits, k=3))
        return key

    def admin_menu(self):
        password = input("Admin-Passwort eingeben: ")
        if password != self.admin_password:
            print("❌ Falsches Passwort!")
            input("Drücken Sie Enter, um fortzufahren...")
            return
        
        while True:
            self.clear_screen()
            print("=" * 50)
            print("           ADMIN-MENÜ")
            print("=" * 50)
            print("Aktive Keys:", len(self.valid_keys))
            for key in self.valid_keys:
                print(f"  - {key}")
            print("=" * 50)
            print("Optionen:")
            print("[1] Neuen Key für externe Benutzer erstellen")
            print("[2] Key löschen")
            print("[3] Admin-Passwort ändern")
            print("[4] Zurück zum Hauptmenü")
            
            choice = input("\n➤ Ihre Wahl: ")
            
            if choice == "1":
                new_key = self.generate_key()
                self.valid_keys[new_key] = True
                self.save_keys()
                print(f"✅ Neuer Key erstellt: {new_key}")
                print("⚠️  Geben Sie diesen Key an externe Benutzer weiter!")
                input("Drücken Sie Enter, um fortzufahren...")
                
            elif choice == "2":
                if self.valid_keys:
                    key_to_delete = input("Geben Sie den zu löschenden Key ein: ")
                    if key_to_delete in self.valid_keys and key_to_delete != self.master_key:
                        del self.valid_keys[key_to_delete]
                        self.save_keys()
                        print(f"✅ Key '{key_to_delete}' wurde gelöscht.")
                    elif key_to_delete == self.master_key:
                        print("❌ Master-Key kann nicht gelöscht werden!")
                    else:
                        print("❌ Key nicht gefunden!")
                    input("Drücken Sie Enter, um fortzufahren...")
                else:
                    print("❌ Keine Keys vorhanden!")
                    input("Drücken Sie Enter, um fortzufahren...")
                    
            elif choice == "3":
                new_password = input("Neues Admin-Passwort: ")
                self.admin_password = new_password
                print("✅ Admin-Passwort wurde geändert.")
                input("Drücken Sie Enter, um fortzufahren...")
                
            elif choice == "4":
                break
                
            else:
                print("❌ Ungültige Auswahl!")
                input("Drücken Sie Enter, um fortzufahren...")
    
    def run(self):
        # Key-Abfrage für externe Benutzer
        if not self.activated:
            self.clear_screen()
            print("=" * 50)
            print("           PC CLEANER TOOL - AKTIVIERUNG")
            print("=" * 50)
            print("Bitte geben Sie Ihren Aktivierungs-Key ein")
            print("Fragen Sie beim Administrator nach einem Key")
            print("=" * 50)
            
            key = input("Key: ")
            
            if key in self.valid_keys:
                self.activated = True
                print("✅ Aktivierung erfolgreich!")
                input("Drücken Sie Enter, um fortzufahren...")
            else:
                print("❌ Ungültiger Key! Das Programm wird beendet.")
                input("Drücken Sie Enter, um fortzufahren...")
                sys.exit()
        
        # Hauptmenü
        while True:
            self.clear_screen()
            self.display_header()
            self.display_menu()
            
            try:
                choice = input("\n➤ Ihre Wahl: ")
                
                if choice == "22":
                    print("Auf Wiedersehen!")
                    break
                elif choice == "21":
                    self.admin_menu()
                elif not self.activated:
                    print("❌ Programm nicht aktiviert!")
                    input("Drücken Sie Enter, um fortzufahren...")
                else:
                    if choice == "1":
                        self.clear_recycle_bin()
                    elif choice == "2":
                        self.clear_temp_folder()
                    elif choice == "3":
                        self.clear_prefetch()
                    elif choice == "4":
                        self.clear_browser_cache()
                    elif choice == "5":
                        self.clear_downloads()
                    elif choice == "7":
                        self.clear_clipboard()
                    elif choice == "13":
                        self.flush_dns()
                    else:
                        print("❌ Diese Funktion ist noch nicht implementiert.")
                    
                    input("\nDrücken Sie Enter, um fortzufahren...")
                    
            except Exception as e:
                print(f"❌ Ein Fehler ist aufgetreten: {e}")
                input("Drücken Sie Enter, um fortzufahren...")

if __name__ == "__main__":
    cleaner = PCCleaner()
    cleaner.run()
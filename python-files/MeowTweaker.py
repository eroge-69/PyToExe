import customtkinter as ctk
import subprocess
import winreg
import os
import sys
from elevate import elevate

# Піднімаємо права адміна, якщо потрібно
elevate(show_console=False)

class MeowTweaker(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("MeowTweaker 🐱")
        self.geometry("900x550")
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        # Бічна панель
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        self.content = ctk.CTkFrame(self, corner_radius=10)
        self.content.pack(side="right", fill="both", expand=True)

        # Кнопки у меню
        ctk.CTkButton(self.sidebar, text="Old Right Click Menu", command=self.enable_old_menu).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="Remove Ads", command=self.remove_ads).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="Show File Extensions", command=self.show_extensions).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="Change Selection Color", command=self.change_selection_color).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="Run Command", command=self.run_command_ui).pack(pady=10, padx=20)

        # Поле для виводу
        self.output = ctk.CTkTextbox(self.content)
        self.output.pack(fill="both", expand=True, padx=20, pady=20)

    def log(self, text: str):
        self.output.insert("end", text + "\n")
        self.output.see("end")

    # --- Tweaks ---
    def enable_old_menu(self):
        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                                   r"Software\\Classes\\CLSID\\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\\InprocServer32")
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "")
            winreg.CloseKey(key)
            self.log("✔ Old context menu enabled. Restart Explorer.")
        except Exception as e:
            self.log(f"❌ Error: {e}")

    def remove_ads(self):
        try:
            # Вимикаємо рекомендації в Start/Search
            subprocess.run([
                "reg", "add", r"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager",
                "/v", "SubscribedContent-338389Enabled", "/t", "REG_DWORD", "/d", "0", "/f"
            ], check=True)
            self.log("✔ Ads removed from Start & Search.")
        except Exception as e:
            self.log(f"❌ Error: {e}")

    def show_extensions(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r"Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "HideFileExt", 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(key)
            self.log("✔ File extensions are now visible.")
        except Exception as e:
            self.log(f"❌ Error: {e}")

    def change_selection_color(self):
        try:
            # Синій колір для виділення (як приклад)
            subprocess.run(["reg", "add", r"HKCU\\Control Panel\\Colors",
                            "/v", "Hilight", "/t", "REG_SZ", "/d", "0 120 215", "/f"], check=True)
            self.log("✔ Selection color changed. Reboot may be required.")
        except Exception as e:
            self.log(f"❌ Error: {e}")

    def run_command_ui(self):
        win = ctk.CTkToplevel(self)
        win.title("Run Command")
        win.geometry("400x150")

        entry = ctk.CTkEntry(win, width=350)
        entry.pack(pady=10, padx=10)

        def run_cmd():
            cmd = entry.get()
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
                self.log("✔ Command executed:\n" + result.stdout)
                if result.stderr:
                    self.log("⚠ Errors:\n" + result.stderr)
            except Exception as e:
                self.log(f"❌ Error: {e}")

        ctk.CTkButton(win, text="Run", command=run_cmd).pack(pady=10)

if __name__ == "__main__":
    app = MeowTweaker()
    app.mainloop()

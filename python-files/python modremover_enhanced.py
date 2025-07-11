import os
import shutil
import sys
import datetime
from pathlib import Path
from tkinter import Tk, Button, Label, messagebox, ttk, StringVar

# ===== Konfiguration =====

GTAV_PATH = Path(sys.argv[0]).parent.resolve()  # Verzeichnis, wo das Script liegt
BACKUP_BASE = Path.home() / "Desktop"

# Alle typischen Mod-Dateien & Ordner (erweiterbar)
MOD_FILES = [
    "dinput8.dll", "ScriptHookV.dll", "ScriptHookVDotNet.dll", "openiv.asi",
    "GTAVLauncherBypass.exe", "asi-loader.log", "TrainerV.asi", "SimpleTrainer.asi",
    "Menyoo.asi", "EnhancedNativeTrainer.asi", "NativeTrainer.asi", "LSPDFR.exe",
    "RAGEPluginHook.exe", "ReShade.ini", "dxgi.dll", "ReduxSettings.xml",
    "GTA5_Modded.exe", "GTA5_Crack.exe", "VisualV.asi", "QuantV.asi",
    "FiveM.asi", "RDE.asi"
]

MOD_FOLDERS = [
    "mods", "scripts", "plugins", "menyooStuff", "OpenIV", "native",
    "add-ons", "LSPDFR", "RAGEPluginHook", "reshade-shaders", "update\\x64\\dlcpacks"
]

# Kategorien für Backup-Ordner
CATEGORIES = {
    "ASI": [".asi"],
    "DLLs": [".dll"],
    "Trainer": [".exe"],
    "Logs": [".log"],
    "Menyoo": ["Menyoo.asi", "menyooStuff"],
    "LSPDFR": ["LSPDFR.exe", "LSPDFR"],
    "Misc": []
}

# Mehrsprachige Texte (Deutsch, Englisch, Russisch)
TEXTS = {
    "title": {
        "de": "ModRemover Enhanced",
        "en": "ModRemover Enhanced",
        "ru": "ModRemover Enhanced"
    },
    "btn_backup": {
        "de": "Mods sichern & verschieben",
        "en": "Backup & Move Mods",
        "ru": "Сделать резервную копию и переместить"
    },
    "btn_delete": {
        "de": "Mods dauerhaft löschen",
        "en": "Delete Mods Permanently",
        "ru": "Удалить моды навсегда"
    },
    "btn_preview": {
        "de": "Mods anzeigen (Vorschau)",
        "en": "Preview Mods",
        "ru": "Показать моды (предварительный просмотр)"
    },
    "btn_quit": {
        "de": "Beenden",
        "en": "Quit",
        "ru": "Выход"
    },
    "label_status": {
        "de": "Status:",
        "en": "Status:",
        "ru": "Статус:"
    },
    "msg_backup_done": {
        "de": "✅ Sicherung abgeschlossen!",
        "en": "✅ Backup completed!",
        "ru": "✅ Резервное копирование завершено!"
    },
    "msg_delete_done": {
        "de": "✅ Alle Mods wurden gelöscht!",
        "en": "✅ All mods deleted!",
        "ru": "✅ Все моды удалены!"
    },
    "msg_no_mods": {
        "de": "Keine Mod-Dateien gefunden.",
        "en": "No mod files found.",
        "ru": "Моды не найдены."
    },
    "msg_confirm_delete": {
        "de": "Willst du wirklich alle Mods endgültig löschen?",
        "en": "Are you sure you want to permanently delete all mods?",
        "ru": "Вы уверены, что хотите удалить все моды навсегда?"
    },
    "lang_label": {
        "de": "Sprache:",
        "en": "Language:",
        "ru": "Язык:"
    }
}

# =========================

class ModRemoverApp:

    def _init_(self, root):
        self.root = root
        self.lang = StringVar(value="de")
        self.status_text = StringVar()
        self.status_text.set("")
        self.create_widgets()
        self.root.title(TEXTS["title"][self.lang.get()])

    def create_widgets(self):
        self.label_status = Label(self.root, text=TEXTS["label_status"][self.lang.get()])
        self.label_status.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        self.status_label = Label(self.root, textvariable=self.status_text, anchor="w", justify="left")
        self.status_label.grid(row=1, column=0, columnspan=4, sticky="we", padx=10)

        self.btn_preview = Button(self.root, text=TEXTS["btn_preview"][self.lang.get()], command=self.preview_mods, width=25)
        self.btn_preview.grid(row=2, column=0, padx=10, pady=10)

        self.btn_backup = Button(self.root, text=TEXTS["btn_backup"][self.lang.get()], command=self.backup_mods, width=25)
        self.btn_backup.grid(row=2, column=1, padx=10, pady=10)

        self.btn_delete = Button(self.root, text=TEXTS["btn_delete"][self.lang.get()], command=self.delete_mods, width=25)
        self.btn_delete.grid(row=2, column=2, padx=10, pady=10)

        self.btn_quit = Button(self.root, text=TEXTS["btn_quit"][self.lang.get()], command=self.root.quit, width=10)
        self.btn_quit.grid(row=2, column=3, padx=10, pady=10)

        self.lang_combo = ttk.Combobox(self.root, values=["Deutsch", "English", "Русский"], state="readonly", width=12)
        self.lang_combo.current(0)
        self.lang_combo.grid(row=0, column=3, padx=10, pady=5)
        self.lang_combo.bind("<<ComboboxSelected>>", self.change_language)

    def change_language(self, event=None):
        lang_map = {"Deutsch": "de", "English": "en", "Русский": "ru"}
        sel = self.lang_combo.get()
        if sel in lang_map:
            self.lang.set(lang_map[sel])
            self.update_texts()

    def update_texts(self):
        self.root.title(TEXTS["title"][self.lang.get()])
        self.label_status.config(text=TEXTS["label_status"][self.lang.get()])
        self.btn_preview.config(text=TEXTS["btn_preview"][self.lang.get()])
        self.btn_backup.config(text=TEXTS["btn_backup"][self.lang.get()])
        self.btn_delete.config(text=TEXTS["btn_delete"][self.lang.get()])
        self.btn_quit.config(text=TEXTS["btn_quit"][self.lang.get()])
        self.lang_combo.set({"de":"Deutsch","en":"English","ru":"Русский"}[self.lang.get()])
        self.status_text.set("")

    def scan_mods(self):
        found_files = []
        found_dirs = []
        for f in MOD_FILES:
            if (GTAV_PATH / f).exists():
                found_files.append(f)
        for d in MOD_FOLDERS:
            if (GTAV_PATH / d).exists():
                found_dirs.append(d)
        return found_files, found_dirs

    def preview_mods(self):
        files, dirs = self.scan_mods()
        if not files and not dirs:
            self.status_text.set(TEXTS["msg_no_mods"][self.lang.get()])
            return
        msg = "Gefundene Dateien:\n" if self.lang.get() == "de" else \
              "Found files:\n" if self.lang.get() == "en" else \
              "Найденные файлы:\n"
        msg += "\n".join(files) + "\n\n"
        msg += "Gefundene Ordner:\n" if self.lang.get() == "de" else \
               "Found folders:\n" if self.lang.get() == "en" else \
               "Найденные папки:\n"
        msg += "\n".join(dirs)
        self.status_text.set(msg)

    def backup_mods(self):
        files, dirs = self.scan_mods()
        if not files and not dirs:
            self.status_text.set(TEXTS["msg_no_mods"][self.lang.get()])
            return
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
        backup_folder = BACKUP_BASE / f"GTAV_ModBackup_{timestamp}"
        backup_folder.mkdir(parents=True, exist_ok=True)

        # Backup Kategorien anlegen
        folders = {}
        for cat in CATEGORIES.keys():
            path = backup_folder / cat
            path.mkdir(exist_ok=True)
            folders[cat] = path

        # Dateien sichern
        for file in files:
            src = GTAV_PATH / file
            # Kategorie finden
            dest_cat = "Misc"
            for cat, exts in CATEGORIES.items():
                if file in exts or any(file.endswith(e) for e in exts):
                    dest_cat = cat
                    break
            # Sonderfälle für Ordnernamen als Kategorie
            if file in ["Menyoo.asi"]:
                dest_cat = "Menyoo"
            if file in ["LSPDFR.exe"]:
                dest_cat = "LSPDFR"
            shutil.move(str(src), str(folders[dest_cat] / file))

        # Ordner sichern
        for dir in dirs:
            src_dir = GTAV_PATH / dir
            dest_dir = backup_folder / dir
            if src_dir.is_dir():
                shutil.move(str(src_dir), str(dest_dir))

        self.status_text.set(TEXTS["msg_backup_done"][self.lang.get()])

    def delete_mods(self):
        files, dirs = self.scan_mods()
        if not files and not dirs:
            self.status_text.set(TEXTS["msg_no_mods"][self.lang.get()])
            return
        if not messagebox.askyesno(TEXTS["btn_delete"][self.lang.get()], TEXTS["msg_confirm_delete"][self.lang.get()]):
            return

        for file in files:
            try:
                os.remove(GTAV_PATH / file)
            except Exception as e:
                print(f"Fehler beim Löschen von {file}: {e}")

        for dir in dirs:
            try:
                shutil.rmtree(GTAV_PATH / dir)
            except Exception as e:
                print(f"Fehler beim Löschen von {dir}: {e}")

        self.status_text.set(TEXTS["msg_delete_done"][self.lang.get()])


def main():
    root = Tk()
    root.geometry("700x250")
    root.resizable(False, False)
    app = ModRemoverApp(root)
    root.mainloop()


if _name_ == "_main_":
    main()
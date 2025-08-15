import os
import threading
import urllib.request
from urllib.error import URLError, HTTPError
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from io import BytesIO
import json
import requests
import zipfile
import time

APP_TITLE = "MSC Manager"
TG_URL = "https://t.me/+aet5vrADyxcyZjVi"
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1405913970925244541/TOrewhIDcPAyCeFjyXwN82abU2lCtPksnKY6615KPG1GF6jwyVUL6uASYb1KOScWfo7k"

# ---------- Загрузка изображений из GitHub ----------
def load_image_from_github(url, size):
    try:
        with urllib.request.urlopen(url) as response:
            img_data = response.read()
        img = Image.open(BytesIO(img_data)).resize(size)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Ошибка загрузки {url}: {e}")
        return None

# ---------- Ссылки на загрузки ----------
DOWNLOAD_URLS = {
    "save_built_car": "https://github.com/Timoshechka-rgb/SAVEE/archive/refs/heads/builtcar.zip",
    "save_disassembled_car": "https://github.com/Timoshechka-rgb/SAVEE/archive/refs/heads/disassembled.zip",
    "mods": "https://github.com/Timoshechka-rgb/MODS/archive/refs/heads/main.zip",
    "skins": "https://github.com/Timoshechka-rgb/SKIN/archive/refs/heads/main.zip",
    "loader": "https://github.com/Timoshechka-rgb/MSCLOADER/archive/refs/heads/main.zip",
    "cheat": "https://github.com/Timoshechka-rgb/Cheat/archive/refs/heads/main.zip",
    "boltsize": "https://github.com/Timoshechka-rgb/BoltSIze/archive/refs/heads/main.zip",
    "russifier": "https://github.com/Timoshechka-rgb/RUSIFIKATOR/archive/refs/heads/main.zip",
    "backpack": "https://github.com/Timoshechka-rgb/BackPAckC/archive/refs/heads/main.zip"
}

# ---------- Переводы ----------
STRINGS = {
    "uk": {
        "main_menu": "Головне меню",
        "save": "Сейв",
        "mods": "Моди",
        "loader": "MSC Лоадер",
        "skins": "Скіни",
        "back": "Назад",
        "settings": "Налаштування",
        "complaint": "Жалоба / Зв'язок",
        "send": "Відправити",
        "choose_folder": "Виберіть папку для збереження",
        "downloading": "Завантаження...",
        "done": "Готово! Файл збережено у: {path}",
        "error": "Помилка завантаження: {err}",
        "loading_text": "Завантаження MSC Manager..."
    },
    "ru": {
        "main_menu": "Главное меню",
        "save": "Сейв",
        "mods": "Моды",
        "loader": "MSC Лоадер",
        "skins": "Скины",
        "back": "Назад",
        "settings": "Настройки",
        "complaint": "Жалоба / Связь",
        "send": "Отправить",
        "choose_folder": "Выберите папку для сохранения",
        "downloading": "Загрузка...",
        "done": "Готово! Файл сохранён в: {path}",
        "error": "Ошибка загрузки: {err}",
        "loading_text": "Загрузка MSC Manager..."
    },
    "en": {
        "main_menu": "Main Menu",
        "save": "Save",
        "mods": "Mods",
        "loader": "MSC Loader",
        "skins": "Skins",
        "back": "Back",
        "settings": "Settings",
        "complaint": "Complaint / Contact",
        "send": "Send",
        "choose_folder": "Choose a folder to save",
        "downloading": "Downloading...",
        "done": "Done! File saved to: {path}",
        "error": "Download error: {err}",
        "loading_text": "Loading MSC Manager..."
    }
}

# ---------- Кнопка ----------
class GlowButton:
    def __init__(self, canvas, x, y, w, h, text, command):
        self.canvas = canvas
        self.command = command
        self.text = text
        self.x, self.y, self.w, self.h = x, y, w, h
        self.radius = 25
        self.rect = self.rounded_rect(x, y, w, h, self.radius, fill="#1a1a1a", outline="#111", width=2)
        self.label = self.canvas.create_text(x + w//2, y + h//2, text=text, fill="#f5f5f5", font=("Segoe UI", 14, "bold"))
        self.canvas.tag_bind(self.rect, "<Button-1>", lambda e: self.click())
        self.canvas.tag_bind(self.label, "<Button-1>", lambda e: self.click())
        self.canvas.tag_bind(self.rect, "<Enter>", lambda e: self.on_hover(True))
        self.canvas.tag_bind(self.rect, "<Leave>", lambda e: self.on_hover(False))
        self.canvas.tag_bind(self.label, "<Enter>", lambda e: self.on_hover(True))
        self.canvas.tag_bind(self.label, "<Leave>", lambda e: self.on_hover(False))

    def rounded_rect(self, x, y, w, h, r, **kwargs):
        points = [
            x+r, y,
            x+w-r, y,
            x+w, y,
            x+w, y+r,
            x+w, y+h-r,
            x+w, y+h,
            x+w-r, y+h,
            x+r, y+h,
            x, y+h,
            x, y+h-r,
            x, y+r,
            x, y
        ]
        return self.canvas.create_polygon(points, smooth=True, **kwargs)

    def on_hover(self, hover):
        color = "#2dd4bf" if hover else "#1a1a1a"
        self.canvas.itemconfig(self.rect, outline=color)
        text_color = "#a7f3d0" if hover else "#f5f5f5"
        self.canvas.itemconfig(self.label, fill=text_color)

    def click(self):
        self.command()

# ---------- Загрузчик ----------
class Downloader(threading.Thread):
    def __init__(self, url, dest_folder, progress_cb, done_cb, error_cb, chunk=1024*64):
        super().__init__(daemon=True)
        self.url = url
        self.dest_folder = dest_folder
        self.progress_cb = progress_cb
        self.done_cb = done_cb
        self.error_cb = error_cb
        self.chunk = chunk

    def run(self):
        try:
            os.makedirs(self.dest_folder, exist_ok=True)
            filename = self.url.strip('/').split('/')[-1]
            if not filename.lower().endswith('.zip'):
                filename += '.zip'
            dest_path = os.path.join(self.dest_folder, filename)
            with urllib.request.urlopen(self.url) as r, open(dest_path, 'wb') as out:
                total = r.getheader('Content-Length')
                total = int(total) if total else None
                read = 0
                while True:
                    chunk = r.read(self.chunk)
                    if not chunk:
                        break
                    out.write(chunk)
                    read += len(chunk)
                    if total:
                        pct = int(read * 100 / total)
                        self.progress_cb(pct)
            self.progress_cb(100)
            self.done_cb(dest_path)
        except (HTTPError, URLError, OSError) as e:
            self.error_cb(str(e))

# ---------- Приложение ----------
class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_TITLE)
        self.root.geometry("1024x600")
        self.root.resizable(False, False)
        self.lang = "uk"
        self.strs = STRINGS[self.lang]

        self.canvas = tk.Canvas(self.root, width=1024, height=600, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.bg_photo = load_image_from_github("https://raw.githubusercontent.com/Timoshechka-rgb/photo/main/msc_background.jpg", (1024, 600))
        if self.bg_photo:
            self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

        self.loading_rect = self.canvas.create_rectangle(150, 500, 874, 530, fill="#111", outline="#222", width=2)
        self.loading_fill = self.canvas.create_rectangle(150, 500, 150, 530, fill="#2dd4bf", outline="")
        self.loading_text = self.canvas.create_text(512, 470, text=self.strs["loading_text"], fill="#f5f5f5", font=("Segoe UI", 20, "bold"))

        self.left_anime_photo = load_image_from_github("https://raw.githubusercontent.com/Timoshechka-rgb/photo/main/anime_girl.png", (250, 600))
        if self.left_anime_photo:
            self.left_anime_id = self.canvas.create_image(0, 0, image=self.left_anime_photo, anchor="nw")

        self.right_anime_photo = load_image_from_github("https://raw.githubusercontent.com/Timoshechka-rgb/photo/main/anime_tyan.png", (250, 600))
        if self.right_anime_photo:
            self.right_anime_id = self.canvas.create_image(1024-250, 0, image=self.right_anime_photo, anchor="nw")

        self.root.after(100, self.fake_loading)
        self.root.mainloop()

    def fake_loading(self):
        steps = 500
        for i in range(steps+1):
            pct = i/steps
            self.canvas.coords(self.loading_fill, 150, 500, 150 + int(724*pct), 530)
            self.root.update()
            time.sleep(0.02)

        self.canvas.delete(self.loading_fill)
        self.canvas.delete(self.loading_rect)
        self.canvas.delete(self.loading_text)
        self.canvas.delete(getattr(self, "left_anime_id", None))
        self.canvas.delete(getattr(self, "right_anime_id", None))
        self.replace_anime_images()
        self.show_main_menu()

    def replace_anime_images(self):
        self.msc_photo = load_image_from_github("https://raw.githubusercontent.com/Timoshechka-rgb/photo/main/msc_znak.png", (250, 250))
        if self.msc_photo:
            self.canvas.create_image(0, 0, image=self.msc_photo, anchor="nw")

        self.new_anime_photo = load_image_from_github("https://raw.githubusercontent.com/Timoshechka-rgb/photo/main/n_anime.png", (250, 600))
        if self.new_anime_photo:
            self.canvas.create_image(1024-250, 0, image=self.new_anime_photo, anchor="nw")

    def show_main_menu(self):
        self.buttons = []
        y_start = 50
        spacing = 70
        self.add_button(310, y_start, "save", self.show_saves)
        self.add_button(310, y_start+spacing, "mods", self.show_mods)
        self.add_button(310, y_start+2*spacing, "skins", lambda: self.choose_and_download('skins'))
        self.add_button(310, y_start+3*spacing, "loader", lambda: self.choose_and_download('loader'))
        self.add_button(310, y_start+4*spacing, "settings", self.show_settings)
        self.add_button(310, y_start+5*spacing, "complaint", self.show_complaint)

    def show_saves(self):
        self.clear_buttons()
        self.add_button(310, 50, "Машина складена + гроші", lambda: self.choose_and_download('save_built_car'))
        self.add_button(310, 120, "Гроші + розібрана машина", lambda: self.choose_and_download('save_disassembled_car'))
        self.add_button(310, 190, "back", self.show_main_menu)

    def show_mods(self):
        self.clear_buttons()
        mods = [
            ("cheat","Cheat"),
            ("boltsize","BoltSize"),
            ("russifier","Russifier"),
            ("backpack","Рюкзак")
        ]
        for i,(key,name) in enumerate(mods):
            self.add_button(310, 50+i*70, key, lambda k=key: self.choose_and_download(k))
        self.add_button(310, 50+len(mods)*70, "back", self.show_main_menu)

    def add_button(self, x, y, key, command):
        text = self.strs.get(key,key)
        btn = GlowButton(self.canvas, x, y, 400, 50, text, command)
        if not hasattr(self, "buttons"):
            self.buttons = []
        self.buttons.append(btn)

    def choose_and_download(self, key):
        url = DOWNLOAD_URLS.get(key)
        if not url:
            messagebox.showwarning(APP_TITLE, 'URL not set')
            return
        folder = filedialog.askdirectory(title=self.strs['choose_folder'])
        if not folder:
            return

        def on_progress(pct):
            pass

        def on_done(path):
            try:
                if path.lower().endswith(".zip"):
                    with zipfile.ZipFile(path, 'r') as zip_ref:
                        zip_ref.extractall(folder)
                    os.remove(path)
                messagebox.showinfo(APP_TITLE, self.strs['done'].format(path=folder))
            except Exception as e:
                messagebox.showerror(APP_TITLE, f"Ошибка распаковки: {e}")

        def on_error(err):
            messagebox.showerror(APP_TITLE, self.strs['error'].format(err=err))

        Downloader(url, folder, on_progress, on_done, on_error).start()

    def show_settings(self):
        self.clear_buttons()
        langs = [("uk", "Українська"), ("ru", "Русский"), ("en", "English")]
        for i, (code, name) in enumerate(langs):
            self.add_button(310, 50 + i * 70, name, lambda c=code: self.set_lang(c))
        self.add_button(310, 50 + len(langs) * 70, "back", self.show_main_menu)

    def set_lang(self, lang):
        self.lang = lang
        self.strs = STRINGS[lang]
        self.show_main_menu()

    def show_complaint(self):
        self.clear_buttons()
        self.textbox = tk.Text(self.root, width=80, height=15, bg="#111", fg="#f5f5f5", font=("Segoe UI", 12))
        self.textbox.place(x=150, y=100)
        self.add_button(310, 450, "send", self.send_complaint)
        self.add_button(310, 520, "back", self.close_complaint)

    def send_complaint(self):
        text = self.textbox.get("1.0","end").strip()
        if not text:
            messagebox.showwarning(APP_TITLE, "Введіть текст для відправки!")
            return
        try:
            data = {"content": text}
            requests.post(DISCORD_WEBHOOK, data=json.dumps(data), headers={"Content-Type":"application/json"})
            messagebox.showinfo(APP_TITLE, "Відправлено!")
            self.close_complaint()
        except Exception as e:
            messagebox.showerror(APP_TITLE, f"Помилка: {e}")

    def close_complaint(self):
        if hasattr(self, "textbox"):
            self.textbox.destroy()
            del self.textbox
        self.show_main_menu()

    def clear_buttons(self):
        if hasattr(self, "buttons"):
            for btn in self.buttons:
                self.canvas.delete(btn.rect)
                self.canvas.delete(btn.label)
            self.buttons.clear()

if __name__ == "__main__":
    App()

import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime
from PIL import Image
import pytesseract
import customtkinter as ctk
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import threading
import vlc
import platform

# ——— CONFIG ———
THUMB_SIZE = (100, 100)
MEDIA_EXTS = {
    "image": (".jpg", ".jpeg", ".png", ".gif"),
    "video": (".mp4", ".webm", ".ogg"),
    "audio": (".mp3", ".wav", ".flac", ".aac")
}
SCROLL_PAUSE = 1  # secs between scrolls

# ——— UTILITIES ———
def fetch_rendered_html(url):
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=opts)
    driver.get(url)
    last_h = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE)
        new_h = driver.execute_script("return document.body.scrollHeight")
        if new_h == last_h:
            break
        last_h = new_h
    html = driver.page_source
    driver.quit()
    return html

def open_file(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        os.system(f'open "{path}"')
    else:
        os.system(f'xdg-open "{path}"')

# ——— DOWNLOAD + OCR ———
def download_media(raw_url):
    # normalize URL
    p = urlparse(raw_url)
    if not p.scheme:
        raw_url = "http://" + raw_url

    base = os.path.dirname(os.path.abspath(__file__))
    outdir = os.path.join(base, "FrickVids")
    os.makedirs(outdir, exist_ok=True)

    try:
        html = fetch_rendered_html(raw_url)
    except Exception as e:
        return [], f"Selenium failed: {e}"

    soup = BeautifulSoup(html, "html.parser")
    found = set()

    # scrape <img>, <video>, <audio> + <source>
    for tag, attr in [("img","src"),("video","src"),("audio","src")]:
        for el in soup.find_all(tag):
            src = el.get(attr)
            if src:
                found.add(urljoin(raw_url, src))
        if tag in ("video","audio"):
            for src_el in soup.find_all("source"):
                src = src_el.get("src")
                if src:
                    found.add(urljoin(raw_url, src))

    # direct links
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if any(href.lower().endswith(ext)
               for exts in MEDIA_EXTS.values() for ext in exts):
            found.add(urljoin(raw_url, href))

    if not found:
        return [], "No media found."

    media_info = []
    for i, murl in enumerate(sorted(found), start=1):
        try:
            r = requests.get(murl, stream=True, timeout=10)
            r.raise_for_status()
        except:
            continue

        path = urlparse(murl).path
        _, ext = os.path.splitext(path)
        if not ext:
            ct = r.headers.get("content-type","")
            if "/" in ct:
                ext = "." + ct.split("/")[-1].split(";")[0]

        fname = f"{i}{ext}"
        fpath = os.path.join(outdir, fname)
        with open(fpath, "wb") as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)

        stat = os.stat(fpath)
        mtype = (
            "image" if ext.lower() in MEDIA_EXTS["image"] else
            "video" if ext.lower() in MEDIA_EXTS["video"] else
            "audio" if ext.lower() in MEDIA_EXTS["audio"] else
            "other"
        )

        # thumbnail + OCR for images
        thumb = None
        ocr_text = ""
        if mtype == "image":
            try:
                img = Image.open(fpath)
                img.thumbnail(THUMB_SIZE)
                thumb_name = f"thumb_{fname}"
                thumb_path = os.path.join(outdir, thumb_name)
                img.save(thumb_path)
                thumb = thumb_path
                # OCR
                ocr_text = pytesseract.image_to_string(img).strip().replace("\n"," ")
            except:
                thumb = fpath

        media_info.append({
            "filename": fname,
            "filepath": fpath,
            "thumb": thumb,
            "type": mtype,
            "src": murl,
            "size_kb": round(stat.st_size/1024,1),
            "downloaded": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "ocr": ocr_text.lower()
        })

    return media_info, None

# ——— APP UI ———
class FrickApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Frick Downloader")
        self.geometry("900x650")

        # theme toggle
        self.theme_menu = ctk.CTkOptionMenu(
            self, values=["System","Light","Dark"],
            command=lambda m: ctk.set_appearance_mode(m))
        self.theme_menu.set("System")
        self.theme_menu.pack(pady=(10,0))

        # URL entry + button
        self.url_entry = ctk.CTkEntry(self, placeholder_text="Enter URL…")
        self.url_entry.pack(fill="x", padx=20, pady=(10,0))
        self.frick_btn = ctk.CTkButton(self, text="Frick", command=self.start_download)
        self.frick_btn.pack(pady=10)

        # search box
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            self, textvariable=self.search_var,
            placeholder_text="Search filename, URL, type, or OCR…")
        self.search_entry.pack(fill="x", padx=20, pady=(0,10))
        self.search_entry.bind("<KeyRelease>", lambda e: self.filter_items())

        # status label
        self.status = ctk.CTkLabel(self, text="")
        self.status.pack()

        # scrollable gallery frame
        self.gallery = ctk.CTkScrollableFrame(self, width=860, height=450)
        self.gallery.pack(padx=20, pady=20)
        self.items = []

    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            self.status.configure(text="Please enter a URL!", text_color="red")
            return
        self.frick_btn.configure(state="disabled")
        self.status.configure(text="Downloading…", text_color="black")
        threading.Thread(target=self.run_download, args=(url,), daemon=True).start()

    def run_download(self, url):
        media_info, error = download_media(url)
        if error:
            self.after(0, lambda: self.status.configure(text=error, text_color="red"))
        else:
            txt = f"Downloaded {len(media_info)} items"
            self.after(0, lambda: self.status.configure(text=txt, text_color="green"))
            self.after(0, lambda: self.populate_gallery(media_info))
        self.after(0, lambda: self.frick_btn.configure(state="normal"))

    def populate_gallery(self, items):
        # clear existing
        for w in self.gallery.winfo_children():
            w.destroy()
        self.items.clear()

        for info in items:
            frame = ctk.CTkFrame(self.gallery, corner_radius=8)
            frame.pack(padx=10, pady=10, fill="x")

            # thumbnail
            if info["type"] == "image" and info["thumb"]:
                img = Image.open(info["thumb"])
                ctk_img = ctk.CTkImage(img, size=THUMB_SIZE)
                lbl = ctk.CTkLabel(frame, image=ctk_img)
                lbl.image = ctk_img
                lbl.pack(side="left", padx=10, pady=10)
            else:
                lbl = ctk.CTkLabel(frame, text=f"[{info['type'].upper()}]")
                lbl.pack(side="left", padx=10, pady=10)

            # details
            details = (
                f"{info['filename']}\n"
                f"{info['size_kb']} KB • {info['downloaded']}\n"
                f"{info['type'].upper()}\n"
                f"OCR: {info['ocr'][:30]}{'…' if len(info['ocr'])>30 else ''}"
            )
            d_lbl = ctk.CTkLabel(frame, text=details, justify="left")
            d_lbl.pack(side="left", padx=10)

            # buttons
            btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
            btn_frame.pack(side="right", padx=10, pady=10)
            open_btn = ctk.CTkButton(
                btn_frame, text="Open", width=70,
                command=lambda p=info["filepath"]: open_file(p))
            open_btn.pack(pady=2)
            prev_btn = ctk.CTkButton(
                btn_frame, text="Preview", width=70,
                command=lambda i=info: self.preview_media(i))
            prev_btn.pack(pady=2)

            self.items.append({"frame": frame, "info": info})

    def filter_items(self):
        q = self.search_var.get().lower()
        for it in self.items:
            txt = (
                it["info"]["filename"].lower() + " " +
                it["info"]["src"].lower() + " " +
                it["info"]["type"] + " " +
                it["info"]["ocr"]
            )
            visible = (q in txt)
            it["frame"].pack_forget() if not visible else it["frame"].pack(
                padx=10, pady=10, fill="x"
            )

    def preview_media(self, info):
        win = ctk.CTkToplevel(self)
        win.title(f"Preview: {info['filename']}")

        if info["type"] == "image":
            img = Image.open(info["filepath"])
            ctk_img = ctk.CTkImage(img, size=(400,400))
            lbl = ctk.CTkLabel(win, image=ctk_img)
            lbl.image = ctk_img
            lbl.pack(padx=10, pady=10)
        else:
            # embed VLC player
            instance = vlc.Instance()
            player = instance.media_player_new()
            media = instance.media_new(info["filepath"])
            player.set_media(media)

            # need a frame to attach video output
            vid_frame = ctk.CTkFrame(win, width=600, height=400)
            vid_frame.pack(padx=10, pady=10)
            win.update()  # ensure window exists
            if platform.system() == "Windows":
                player.set_hwnd(vid_frame.winfo_id())
            else:
                player.set_xwindow(vid_frame.winfo_id())

            player.play()

if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = FrickApp()
    app.mainloop()

import os
import random
import threading
import requests
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from moviepy.editor import ImageSequenceClip

API_KEY = "17005766-90b2ef0c8f0657c3d285bb899"
MAX_PER_QUERY = 200
STOP_DOWNLOAD = False

RANDOM_WORDS = [
    "Earth", "ground", "soil", "dirt", "rock", "stone", "pebble", "sand", "dust", "mud", "clay", "land", "field", "grass", "meadow",
    "hill", "slope", "rise", "fall", "peak", "crest", "summit", "top", "base", "foot", "cliff", "ridge", "valley", "gorge", "canyon",
    "plain", "desert", "oasis", "dune", "cave", "tunnel", "cavern", "mountain", "range", "forest", "wood", "grove", "tree", "trunk",
    "branch", "leaf", "bark", "root", "vine", "bush", "shrub", "plant", "flower", "bloom", "petal", "bud", "seed", "moss", "fern", "lichen",
    "path", "trail", "road", "track", "clear", "open", "vast", "narrow", "deep", "hollow", "ancient", "wild", "hidden", "secret", "lush",
    "green", "barren", "desolate", "sky", "air", "wind", "storm", "cloud", "mist", "sun", "light", "dawn", "sunset", "twilight", "night",
    "moon", "star", "galaxy", "space", "infinite", "blue", "golden", "dark", "glow", "sparkle", "thunder", "lightning", "echo", "howl",
    "roar", "float", "soar", "life", "animal", "bird", "fish", "wild", "grow", "bloom", "decay", "hunt", "prey", "fly", "crawl", "nest",
    "home", "habitat", "song", "cry", "leap", "glide", "splash", "hide", "scent", "track", "print", "feather", "scale", "wing", "tooth",
    "shell", "thorn", "algae", "mushroom", "fire", "flame", "heat", "cold", "ice", "snow", "quake", "rumble", "burn", "freeze", "melt",
    "pressure", "breeze", "chill", "aroma", "wet", "dry", "rough", "smooth", "sharp", "loud", "silent", "peace", "serene", "raw", "grand",
    "tiny", "large", "vital", "dead", "pulse", "change", "adapt", "survive", "thrive"
]

class ImageDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pixabay Downloader")
        self.root.geometry("650x400")
        self.root.configure(bg="#1e1e1e")
        self.download_thread = None
        self.output_folder = ""
        self.images_downloaded = []
        self.build_gui()

    def build_gui(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", foreground="white", background="#1e1e1e")
        style.configure("TButton", padding=6)
        style.configure("Green.Horizontal.TProgressbar", troughcolor="#444", background="green")
        style.map("TButton", background=[("active", "#444")], foreground=[("active", "#fff")])

        ttk.Label(self.root, text="Palavra-chave:").grid(row=0, column=0, sticky="w", padx=10, pady=10)
        self.keyword_entry = ttk.Entry(self.root, width=40)
        self.keyword_entry.grid(row=0, column=1, padx=10)

        self.random_button = ttk.Button(self.root, text="Palavra Aleatória", command=self.set_random_keyword)
        self.random_button.grid(row=0, column=2, padx=5)

        ttk.Label(self.root, text="Idioma:").grid(row=1, column=0, sticky="w", padx=10)
        self.lang_var = tk.StringVar(value="pt")
        ttk.OptionMenu(self.root, self.lang_var, "pt", "pt", "en").grid(row=1, column=1, sticky="w")

        ttk.Label(self.root, text="Quantidade de imagens:").grid(row=2, column=0, sticky="w", padx=10)
        self.quantity_spinbox = ttk.Spinbox(self.root, from_=5, to=200, width=10)
        self.quantity_spinbox.grid(row=2, column=1, sticky="w")

        self.select_folder_button = ttk.Button(self.root, text="Selecionar Pasta", command=self.select_folder)
        self.select_folder_button.grid(row=3, column=0, padx=10, pady=10)

        self.start_button = ttk.Button(self.root, text="Iniciar Download", command=self.start_download)
        self.start_button.grid(row=3, column=1, padx=10)

        self.stop_button = ttk.Button(self.root, text="Parar", command=self.stop_download)
        self.stop_button.grid(row=3, column=2)
        self.stop_button.configure(style="Red.TButton")
        style.configure("Red.TButton", background="darkred", foreground="white")

        self.progress = ttk.Progressbar(self.root, length=400, style="Green.Horizontal.TProgressbar")
        self.progress.grid(row=4, column=0, columnspan=3, pady=10)

    def set_random_keyword(self):
        self.keyword_entry.delete(0, tk.END)
        self.keyword_entry.insert(0, random.choice(RANDOM_WORDS))

    def select_folder(self):
        self.output_folder = filedialog.askdirectory()
        if self.output_folder:
            messagebox.showinfo("Pasta selecionada", self.output_folder)

    def start_download(self):
        global STOP_DOWNLOAD
        STOP_DOWNLOAD = False

        keyword = self.keyword_entry.get().strip()
        lang = self.lang_var.get()
        try:
            quantity = int(self.quantity_spinbox.get())
        except ValueError:
            messagebox.showerror("Erro", "Quantidade inválida")
            return

        if not keyword:
            messagebox.showerror("Erro", "Digite uma palavra-chave")
            return
        if not self.output_folder:
            messagebox.showerror("Erro", "Escolha uma pasta de destino")
            return

        self.download_thread = threading.Thread(
            target=self.download_images,
            args=(keyword, lang, quantity),
            daemon=True
        )
        self.download_thread.start()

    def stop_download(self):
        global STOP_DOWNLOAD
        STOP_DOWNLOAD = True
        messagebox.showinfo("Interrompido", "Download interrompido.")

    def download_images(self, keyword, lang, quantity):
        self.images_downloaded = []
        self.progress["value"] = 0
        page = 1

        while len(self.images_downloaded) < quantity and not STOP_DOWNLOAD:
            url = (
                f"https://pixabay.com/api/?key={API_KEY}&q={keyword}&lang={lang}"
                f"&image_type=photo&orientation=horizontal&page={page}&per_page=100"
            )
            resp = requests.get(url).json()
            hits = resp.get("hits", [])

            if not hits:
                break

            for img in hits:
                if len(self.images_downloaded) >= quantity or STOP_DOWNLOAD:
                    break
                image_url = img["webformatURL"]
                try:
                    img_data = requests.get(image_url).content
                    filename = f"{keyword}_{len(self.images_downloaded):03d}.jpg"
                    path = os.path.join(self.output_folder, filename)
                    with open(path, "wb") as f:
                        f.write(img_data)
                    self.images_downloaded.append(path)
                    self.progress["value"] = len(self.images_downloaded) * 100 / quantity
                except Exception as e:
                    print("Erro ao baixar:", e)

            page += 1

        if self.images_downloaded:
            self.create_videos()

        if not STOP_DOWNLOAD:
            messagebox.showinfo("Concluído", f"{len(self.images_downloaded)} imagens baixadas e vídeos criados.")
        else:
            messagebox.showwarning("Parado", f"{len(self.images_downloaded)} imagens baixadas antes de parar.")

    def create_videos(self):
        total_images = self.images_downloaded.copy()
        random.shuffle(total_images)
        video_count = max(2, len(total_images) // 6)

        for i in range(video_count):
            if not total_images:
                break

            num_imgs = random.randint(5, min(10, len(total_images)))
            selected_imgs = random.sample(total_images, num_imgs)
            for img in selected_imgs:
                total_images.remove(img)

            duration = random.uniform(45, 180)  # seconds
            frame_duration = duration / (2 * len(selected_imgs))  # because of boomerang

            clip = ImageSequenceClip(selected_imgs + selected_imgs[::-1], durations=[frame_duration]*len(selected_imgs)*2)
            clip = clip.resize((854, 480))  # 480p
            clip.write_videofile(os.path.join(self.output_folder, f"video_{i+1}.mp4"), fps=24, audio=False, verbose=False, logger=None)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageDownloaderApp(root)
    root.mainloop()

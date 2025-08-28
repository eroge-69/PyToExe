import tkinter as tk
import tkinter.font as tkfont
from tkinter import filedialog, messagebox
import pygame
import os
import random
import time
import json
import math
import threading
import queue
try:
    from PIL import Image, ImageTk  # Libreria per le icone
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

try:
    from mutagen.mp3 import MP3
    from mutagen.wave import WAVE
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False

try:
    pygame.mixer.init()
except pygame.error as e:
    print(f"Errore inizializzazione Pygame: {e}")
    exit(1)

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Lettore Musicale")
        self.root.geometry("1200x900")
        self.root.minsize(1024, 768)
        self.root.configure(bg="#ffffff")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        try:
            self.root.iconbitmap(os.path.join(os.path.dirname(__file__), "icon.ico"))
        except tk.TclError:
            try:
                self.root.iconphoto(True, tk.PhotoImage(file=os.path.join(os.path.dirname(__file__), "icon.png")))
            except (tk.TclError, FileNotFoundError):
                pass

        # Variabili
        self.playlist = []
        self.current_track_index = -1
        self.is_playing = False
        self.is_paused = False
        self.is_shuffling = False
        self.is_looping = False
        self.is_single_loop = False
        self.current_time = 0
        self.total_duration = 0
        self.start_time = 0
        self.beat_frequency = 2.0
        self.beat_amplitude = 0.0
        self.target_amplitude = 0.0
        self.amplitude_transition_start = 0
        self.music_folder = r"C:\Users\atteo\Music\Playlists\musica Anbernic"
        self.is_seeking = False
        self.seek_supported = True
        self.debug_log = True
        self.theme_colors = {
            "bg": "#ffffff",
            "button": "#e0e0e0",
            "button_hover": "#d0d0d0",
            "disabled": "#cccccc",
            "highlight": "#add8e6",
            "progress": "#90ee90",
            "trough": "#cccccc",
            "label": "#ffffff",
            "scale_bg": "#e0e0e0",
            "list_fg": "#000000",
            "select": "#cccccc",
            "progress_frame_bg": "#ffffff",
            "volume_frame_bg": "#ffffff",
            "controls_frame_bg": "#ffffff",
            "listbox_border": "#000000",
            "shadow": "#b0b0b0"
        }
        self.default_colors = self.theme_colors.copy()
        self.shuffle_history = []
        self.last_interaction = time.time()
        self.idle_timeout = 20
        self.is_rgb_mode = False
        self.rgb_timer = None
        self.idle_timer = None
        self.current_rgb = {key: self.hex_to_rgb(self.theme_colors[key]) for key in self.theme_colors}
        self.target_rgb = self.current_rgb.copy()
        self.transition_steps = 50
        self.is_fullscreen = False
        self.notification = None
        self.notification_queue = []
        self.is_minimized = False
        self.notification_timer = None
        self.metadata_cache = {}  # {path: {"display": str, "artist": str, "title": str, "duration": float, "timestamp": float}}
        self.seek_label = None
        self.fps_target = 30
        self.last_frame_time = time.time()
        self.metadata_queue = queue.Queue()
        self.icons = {}
        self.ui_initialized = False
        self.config_file = "config.json"
        self.window_sizes = ["1024x768", "1280x720", "1440x900", "1920x1080"]
        self.current_window_size = "1200x900"

        # Creazione UI
        try:
            self.create_ui()
            self.ui_initialized = True
        except Exception as e:
            self.log_debug(f"Errore inizializzazione UI: {str(e)}")
            messagebox.showerror("Errore", f"Impossibile inizializzare l'interfaccia: {str(e)}")
            self.root.destroy()
            return

        # Caricamento configurazione
        try:
            self.load_config()
        except Exception as e:
            self.log_debug(f"Errore caricamento configurazione in __init__: {str(e)}")

        # Caricamento immediato della playlist
        try:
            self.update_playlist()
        except Exception as e:
            self.log_debug(f"Errore caricamento playlist iniziale: {str(e)}")
            self.status_label.config(text="Errore caricamento playlist")
            messagebox.showerror("Errore", f"Impossibile caricare la playlist: {str(e)}")

        # Avvisi per dipendenze mancanti
        if not MUTAGEN_AVAILABLE:
            messagebox.showwarning("Avviso", "Il modulo 'mutagen' non è installato. La barra di avanzamento e i metadati saranno disabilitati.")
            self.progress_scale.config(state="disabled")
        if not PILLOW_AVAILABLE:
            messagebox.showwarning("Avviso", "Il modulo 'Pillow' non è installato. Le icone non saranno visualizzate.")

        self.show_startup_message()
        self.root.bind("<Unmap>", self.on_minimize)
        self.root.bind("<Map>", self.on_restore)
        self.root.bind("<Configure>", self.update_notification_position)

        self.start_idle_timer()
        self.root.after(200, self.check_metadata_queue)
        self.log_debug(f"Finestra inizializzata: {self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}, DPI: {self.root.winfo_fpixels('1i')}")

    def create_ui(self):
        font_families = tkfont.families()
        self.button_font = tkfont.Font(family="Segoe UI", size=14, weight="bold") if "Segoe UI" in font_families else tkfont.Font(family="Helvetica", size=14, weight="bold")
        self.label_font = tkfont.Font(family="Segoe UI", size=11) if "Segoe UI" in font_families else tkfont.Font(family="Helvetica", size=11)
        self.track_font = tkfont.Font(family="Segoe UI", size=16, weight="bold") if "Segoe UI" in font_families else tkfont.Font(family="Helvetica", size=16, weight="bold")
        self.listbox_font = tkfont.Font(family="Segoe UI", size=10) if "Segoe UI" in font_families else tkfont.Font(family="Helvetica", size=10)
        self.notification_font = tkfont.Font(family="Segoe UI", size=14, weight="bold") if "Segoe UI" in font_families else tkfont.Font(family="Helvetica", size=14, weight="bold")
        self.credit_font = tkfont.Font(family="Segoe UI", size=8) if "Segoe UI" in font_families else tkfont.Font(family="Helvetica", size=8)

        # Caricamento icone
        icon_names = ["play", "pause", "prev", "next", "add", "remove", "rgb", "shuffle", "resize"]
        for name in icon_names:
            if PILLOW_AVAILABLE:
                try:
                    img = Image.open(f"{name}.png").resize((48, 48), Image.LANCZOS)
                    self.icons[name] = ImageTk.PhotoImage(img)
                except Exception as e:
                    self.log_debug(f"Errore caricamento icona {name}.png: {str(e)}")
                    self.icons[name] = None
            else:
                self.icons[name] = None

        # Main frame
        self.main_frame = tk.Frame(self.root, bg=self.theme_colors["bg"])
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Etichetta sviluppatore
        self.credit_label = tk.Label(
            self.main_frame,
            text="Programmato da Antonio Pio Teoli",
            font=self.credit_font,
            bg=self.theme_colors["bg"],
            fg=self.get_text_fg(self.theme_colors["bg"])
        )
        self.credit_label.pack(anchor="nw", padx=10, pady=5)

        # Track info
        self.track_info_label = tk.Label(self.main_frame, text="Nessun brano", font=self.track_font, bg=self.theme_colors["bg"], fg=self.get_text_fg(self.theme_colors["bg"]))
        self.track_info_label.pack(pady=10)

        # Progress bar
        self.progress_frame = tk.Frame(self.main_frame, bg=self.theme_colors["progress_frame_bg"])
        self.progress_frame.pack(fill="x", padx=10)
        self.time_label = tk.Label(self.progress_frame, text="00:00 / 00:00", font=self.label_font, bg=self.theme_colors["progress_frame_bg"], fg=self.get_text_fg(self.theme_colors["progress_frame_bg"]))
        self.time_label.pack()
        self.progress_scale = tk.Scale(self.progress_frame, from_=0, to=100, orient="horizontal", bg=self.theme_colors["scale_bg"], fg=self.get_text_fg(self.theme_colors["scale_bg"]), troughcolor=self.theme_colors["trough"], highlightthickness=0, showvalue=0)
        self.progress_scale.pack(fill="x")
        self.progress_scale.bind("<Button-1>", self.seek_track_start)
        self.progress_scale.bind("<B1-Motion>", self.seek_track)
        self.progress_scale.bind("<ButtonRelease-1>", self.seek_track_release)

        # Controls frame
        self.controls_frame = tk.Frame(self.main_frame, bg=self.theme_colors["controls_frame_bg"])
        self.controls_frame.pack(pady=10)
        button_configs = [
            ("Riproduci", self.play_music, "normal", "play", "▶", "Riproduci brano"),
            ("Pausa", self.pause_music, "disabled", "pause", "⏸", "Metti in pausa"),
            ("Precedente", self.prev_track, "normal", "prev", "⏮", "Brano precedente"),
            ("Successivo", self.next_track, "normal", "next", "⏭", "Brano successivo"),
            ("Aggiungi", self.add_track, "normal", "add", "📂", "Aggiungi brani"),
            ("Rimuovi", self.remove_track, "normal", "remove", "🗑", "Rimuovi brano"),
            ("RGB", self.toggle_rgb_mode, "normal", "rgb", "🌈", "Attiva/Disattiva modalità RGB"),
            ("Shuffle", self.toggle_shuffle, "normal", "shuffle", "🔀", "Attiva/Disattiva shuffle"),
            ("Dimensione", None, "normal", "resize", "🖥️", "Seleziona dimensione finestra")
        ]
        self.buttons = {}
        for label, cmd, state, icon_key, fallback_text, tooltip in button_configs:
            if label == "Dimensione":
                btn_frame = tk.Frame(self.controls_frame, bg=self.theme_colors["controls_frame_bg"])
                btn_frame.pack(side="left", padx=8)
                btn = tk.Button(
                    btn_frame,
                    text=fallback_text if not self.icons.get(icon_key) else "",
                    image=self.icons.get(icon_key),
                    compound="center",
                    font=self.button_font,
                    bg=self.theme_colors["button"],
                    fg=self.get_text_fg(self.theme_colors["button"]),
                    activebackground=self.theme_colors["button_hover"],
                    activeforeground=self.get_text_fg(self.theme_colors["button_hover"]),
                    relief="flat",
                    bd=0,
                    padx=10,
                    pady=5
                )
                btn.pack(side="left")
                btn.bind("<Enter>", lambda e, b=btn: self.on_button_enter(b))
                btn.bind("<Leave>", lambda e, b=btn: self.on_button_leave(b))
                btn.tooltip_text = tooltip
                btn.tooltip_id = None
                self.buttons[label] = btn
                self.size_var = tk.StringVar(value=self.current_window_size)
                size_menu = tk.OptionMenu(
                    btn_frame,
                    self.size_var,
                    *self.window_sizes,
                    command=self.resize_window
                )
                size_menu.config(
                    font=self.button_font,
                    bg=self.theme_colors["button"],
                    fg=self.get_text_fg(self.theme_colors["button"]),
                    activebackground=self.theme_colors["button_hover"],
                    activeforeground=self.get_text_fg(self.theme_colors["button_hover"]),
                    relief="flat",
                    bd=0
                )
                size_menu.pack(side="left", padx=5)
            else:
                btn = tk.Button(
                    self.controls_frame,
                    text=fallback_text if not self.icons.get(icon_key) else "",
                    image=self.icons.get(icon_key),
                    compound="center",
                    font=self.button_font,
                    bg=self.theme_colors["button"] if state == "normal" else self.theme_colors["disabled"],
                    fg=self.get_text_fg(self.theme_colors["button"]),
                    activebackground=self.theme_colors["button_hover"],
                    activeforeground=self.get_text_fg(self.theme_colors["button_hover"]),
                    command=cmd,
                    state=state,
                    relief="flat",
                    bd=0,
                    padx=10,
                    pady=5
                )
                btn.pack(side="left", padx=8)
                btn.bind("<Enter>", lambda e, b=btn: self.on_button_enter(b))
                btn.bind("<Leave>", lambda e, b=btn: self.on_button_leave(b))
                btn.tooltip_text = tooltip
                btn.tooltip_id = None
                self.buttons[label] = btn

        self.play_button = self.buttons["Riproduci"]
        self.pause_button = self.buttons["Pausa"]
        self.prev_button = self.buttons["Precedente"]
        self.next_button = self.buttons["Successivo"]
        self.add_button = self.buttons["Aggiungi"]
        self.remove_button = self.buttons["Rimuovi"]
        self.rgb_button = self.buttons["RGB"]
        self.shuffle_button = self.buttons["Shuffle"]
        self.size_button = self.buttons["Dimensione"]

        # Volume frame
        self.volume_frame = tk.Frame(self.main_frame, bg=self.theme_colors["volume_frame_bg"])
        self.volume_frame.pack(fill="x", pady=10)
        tk.Label(self.volume_frame, text="Volume", font=self.label_font, bg=self.theme_colors["volume_frame_bg"], fg=self.get_text_fg(self.theme_colors["volume_frame_bg"])).pack(side="left", padx=10)
        self.volume_scale = tk.Scale(self.volume_frame, from_=0, to=100, orient="horizontal", bg=self.theme_colors["scale_bg"], fg=self.get_text_fg(self.theme_colors["scale_bg"]), troughcolor=self.theme_colors["trough"], highlightthickness=0, showvalue=0)
        self.volume_scale.set(50)
        self.volume_scale.pack(side="left", fill="x", expand=True, padx=10)
        self.volume_scale.bind("<B1-Motion>", self.set_volume)

        # Playlist
        self.playlist_frame = tk.Frame(self.main_frame, bg=self.theme_colors["bg"])
        self.playlist_frame.pack(fill="both", expand=True)
        self.playlist_box = tk.Listbox(
            self.playlist_frame, font=self.listbox_font, bg="#ffffff",
            fg="#000000", selectbackground=self.theme_colors["select"],
            selectforeground=self.get_text_fg(self.theme_colors["select"]), highlightthickness=1,
            highlightbackground=self.theme_colors["listbox_border"]
        )
        self.playlist_box.pack(side="left", fill="both", expand=True)
        scrollbar = tk.Scrollbar(self.playlist_frame, orient="vertical", command=self.playlist_box.yview)
        scrollbar.pack(side="right", fill="y")
        self.playlist_box.config(yscrollcommand=scrollbar.set)
        self.playlist_box.bind("<Double-1>", self.play_selected_track)

        # Status label
        self.status_label = tk.Label(self.main_frame, text="Nessun brano", font=self.label_font, bg=self.theme_colors["bg"], fg=self.get_text_fg(self.theme_colors["bg"]))
        self.status_label.pack(pady=5)

    def resize_window(self, size):
        if not self.ui_initialized:
            self.log_debug("Tentativo di ridimensionare finestra prima dell'inizializzazione UI")
            return
        try:
            self.current_window_size = size
            self.root.geometry(size)
            self.save_config()
            self.show_notification(f"Finestra ridimensionata a {size}")
            self.log_debug(f"Finestra ridimensionata a {size}")
            self.reset_idle_timer()
            self.update_notification_position()
        except Exception as e:
            self.log_debug(f"Errore ridimensionamento finestra: {str(e)}")
            self.status_label.config(text="Errore durante il ridimensionamento")
            messagebox.showerror("Errore", f"Impossibile ridimensionare la finestra: {str(e)}")

    def update_notification_position(self, event=None):
        if not self.ui_initialized or not self.notification or not self.notification.winfo_exists():
            return
        try:
            self.main_frame.update_idletasks()  # Forza aggiornamento layout
            self.notification.place(
                x=self.main_frame.winfo_width() - 20,
                y=self.main_frame.winfo_height() - 20,
                anchor="se"
            )
        except Exception as e:
            self.log_debug(f"Errore aggiornamento posizione notifica: {str(e)}")

    def load_config(self):
        if not self.ui_initialized:
            self.log_debug("Tentativo di caricare configurazione prima dell'inizializzazione UI")
            return
        try:
            with open(self.config_file, "r") as f:
                config = json.load(f)
                self.music_folder = config.get("music_folder", self.music_folder)
                self.theme_colors = config.get("theme_colors", self.theme_colors)
                self.current_rgb = {key: self.hex_to_rgb(self.theme_colors[key]) for key in self.theme_colors}
                self.target_rgb = self.current_rgb.copy()
                self.is_rgb_mode = config.get("is_rgb_mode", False)
                self.is_shuffling = config.get("is_shuffling", False)
                self.current_window_size = config.get("window_size", self.current_window_size)
                if self.current_window_size in self.window_sizes:
                    self.resize_window(self.current_window_size)
                if self.is_rgb_mode:
                    self.toggle_rgb_mode()
                if self.is_shuffling:
                    self.toggle_shuffle()
                volume = config.get("volume", 50)
                try:
                    self.volume_scale.set(volume)
                    self.set_volume()
                    self.log_debug(f"Volume caricato: {volume}")
                except Exception as e:
                    self.log_debug(f"Errore impostazione volume da configurazione: {str(e)}")
                self.log_debug("Configurazione caricata correttamente")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.log_debug(f"Errore caricamento configurazione: {str(e)}")
            self.save_config()
        except Exception as e:
            self.log_debug(f"Errore imprevisto in load_config: {str(e)}")
            self.current_window_size = "1200x900"
            self.resize_window(self.current_window_size)

    def save_config(self):
        if not self.ui_initialized:
            self.log_debug("Tentativo di salvare configurazione prima dell'inizializzazione UI")
            return
        config = {
            "music_folder": self.music_folder,
            "theme_colors": self.theme_colors,
            "is_rgb_mode": self.is_rgb_mode,
            "is_shuffling": self.is_shuffling,
            "volume": self.volume_scale.get() if hasattr(self, 'volume_scale') else 50,
            "window_size": self.current_window_size
        }
        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=4)
            self.log_debug("Configurazione salvata")
        except Exception as e:
            self.log_debug(f"Errore salvataggio configurazione: {str(e)}")

    def on_button_enter(self, button):
        if button.cget("state") == "normal":
            button.configure(bg=self.theme_colors["button_hover"])
            button.tooltip_id = self.root.after(500, lambda: self.show_tooltip(button))

    def on_button_leave(self, button):
        button.configure(bg=self.theme_colors["button"] if button.cget("state") == "normal" else self.theme_colors["disabled"])
        if button.tooltip_id:
            self.root.after_cancel(button.tooltip_id)
            button.tooltip_id = None
        self.hide_tooltip(button)

    def show_tooltip(self, widget):
        if not hasattr(widget, "tooltip_text") or not widget.winfo_exists():
            return
        try:
            x = widget.winfo_rootx() + 20
            y = widget.winfo_rooty() + 20
            tooltip = tk.Toplevel(widget)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{x}+{y}")
            tk.Label(tooltip, text=widget.tooltip_text, font=("Segoe UI", 10), bg="#f5f5f5", fg="#333333", relief="solid", borderwidth=1).pack()
            widget.tooltip_win = tooltip
        except Exception as e:
            self.log_debug(f"Errore creazione tooltip: {str(e)}")

    def hide_tooltip(self, widget):
        if hasattr(widget, "tooltip_win") and widget.tooltip_win:
            try:
                widget.tooltip_win.destroy()
            except tk.TclError:
                pass
            widget.tooltip_win = None

    def on_closing(self):
        # Annulla tutti i timer
        for timer in [self.rgb_timer, self.idle_timer, self.notification_timer]:
            if timer:
                try:
                    self.root.after_cancel(timer)
                except tk.TclError:
                    pass
        # Distruggi notifiche e seek label
        for widget in [self.notification, self.seek_label]:
            if widget and widget.winfo_exists():
                try:
                    widget.destroy()
                except tk.TclError:
                    pass
        # Distruggi tooltip
        for btn in self.buttons.values():
            self.hide_tooltip(btn)
        # Ferma la musica
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
        except pygame.error:
            pass
        # Salva configurazione
        if self.ui_initialized:
            try:
                self.save_config()
            except Exception as e:
                self.log_debug(f"Errore salvataggio configurazione in on_closing: {str(e)}")
        try:
            self.root.destroy()
        except tk.TclError:
            pass

    def log_debug(self, message):
        if self.debug_log:
            try:
                with open("debug_log.txt", "a", encoding="utf-8") as f:
                    f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
            except Exception as e:
                print(f"Errore scrittura debug log: {str(e)}")

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip("#")
        try:
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except ValueError as e:
            self.log_debug(f"Errore conversione colore hex {hex_color}: {str(e)}")
            return (255, 255, 255)

    def rgb_to_hex(self, rgb):
        try:
            return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        except Exception as e:
            self.log_debug(f"Errore conversione colore RGB {rgb}: {str(e)}")
            return "#ffffff"

    def interpolate_color(self, start_rgb, target_rgb, step, total_steps):
        try:
            r = int(start_rgb[0] + (target_rgb[0] - start_rgb[0]) * step / total_steps)
            g = int(start_rgb[1] + (target_rgb[1] - start_rgb[1]) * step / total_steps)
            b = int(start_rgb[2] + (target_rgb[2] - start_rgb[2]) * step / total_steps)
            return (r, g, b)
        except Exception as e:
            self.log_debug(f"Errore interpolazione colore: {str(e)}")
            return start_rgb

    def generate_random_rgb(self):
        palette = [
            (100, 200, 255),  # Celeste
            (255, 150, 150),  # Rosa chiaro
            (150, 255, 150),  # Verde chiaro
            (255, 200, 100),  # Giallo chiaro
            (200, 150, 255),  # Viola chiaro
            (255, 100, 200),  # Magenta chiaro
            (255, 165, 0),    # Arancione
            (128, 0, 128),    # Viola scuro
            (0, 255, 255),    # Ciano
            (139, 0, 139),    # Magenta scuro
            (0, 128, 0),      # Verde scuro
            (0, 0, 139),      # Blu scuro
            (255, 215, 0),    # Giallo scuro
            (255, 99, 71)     # Rosso chiaro
        ]
        return random.choice(palette)

    def calculate_contrast_ratio(self, fg_rgb, bg_rgb):
        def luminance(rgb):
            try:
                r, g, b = [x / 255.0 for x in rgb]
                r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
                g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
                b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
                return 0.2126 * r + 0.7152 * g + 0.0722 * b
            except Exception as e:
                self.log_debug(f"Errore calcolo luminanza {rgb}: {str(e)}")
                return 0.5
        try:
            lum_fg = luminance(fg_rgb)
            lum_bg = luminance(bg_rgb)
            lum_max, lum_min = max(lum_fg, lum_bg), min(lum_fg, lum_bg)
            return (lum_max + 0.05) / (lum_min + 0.05)
        except Exception as e:
            self.log_debug(f"Errore calcolo rapporto contrasto: {str(e)}")
            return 4.5

    def get_text_fg(self, bg_hex):
        bg_rgb = self.hex_to_rgb(bg_hex)
        white_rgb = (255, 255, 255)
        black_rgb = (0, 0, 0)
        dark_grey = (51, 51, 51)
        light_grey = (221, 221, 221)
        white_contrast = self.calculate_contrast_ratio(white_rgb, bg_rgb)
        black_contrast = self.calculate_contrast_ratio(black_rgb, bg_rgb)
        if white_contrast >= 4.5:
            return "#ffffff"
        elif black_contrast >= 4.5:
            return "#000000"
        else:
            dark_contrast = self.calculate_contrast_ratio(dark_grey, bg_rgb)
            light_contrast = self.calculate_contrast_ratio(light_grey, bg_rgb)
            return "#333333" if dark_contrast >= 4.5 else "#dddddd"

    def change_colors_rgb(self, step=0):
        if not self.is_rgb_mode or not self.ui_initialized or not self.root.winfo_exists():
            return
        if step == 0:
            self.target_rgb = {key: self.generate_random_rgb() for key in self.current_rgb}

        new_colors = {}
        for key in self.current_rgb:
            new_colors[key] = self.interpolate_color(self.current_rgb[key], self.target_rgb[key], step, self.transition_steps)

        for key in self.theme_colors:
            self.theme_colors[key] = self.rgb_to_hex(new_colors[key])

        try:
            self.apply_colors()
        except Exception as e:
            self.log_debug(f"Errore applicazione colori RGB: {str(e)}")

        if step < self.transition_steps:
            self.rgb_timer = self.root.after(30, self.change_colors_rgb, step + 1)
        else:
            self.current_rgb = self.target_rgb.copy()
            self.rgb_timer = self.root.after(2000, self.change_colors_rgb, 0)

    def apply_colors(self):
        if not self.ui_initialized or not self.root.winfo_exists():
            self.log_debug("Tentativo di applicare colori prima dell'inizializzazione UI o dopo chiusura")
            return
        try:
            self.root.configure(bg=self.theme_colors["bg"])
            self.main_frame.configure(bg=self.theme_colors["bg"])
            self.progress_frame.configure(bg=self.theme_colors["progress_frame_bg"])
            self.volume_frame.configure(bg=self.theme_colors["volume_frame_bg"])
            self.controls_frame.configure(bg=self.theme_colors["controls_frame_bg"])
            self.playlist_box.configure(
                bg="#ffffff",
                fg="#000000",
                selectbackground=self.theme_colors["select"],
                selectforeground=self.get_text_fg(self.theme_colors["select"]),
                highlightbackground=self.theme_colors["listbox_border"],
                highlightcolor=self.theme_colors["listbox_border"]
            )
            self.credit_label.configure(bg=self.theme_colors["bg"], fg=self.get_text_fg(self.theme_colors["bg"]))
            self.time_label.configure(bg=self.theme_colors["progress_frame_bg"], fg=self.get_text_fg(self.theme_colors["progress_frame_bg"]))
            self.status_label.configure(bg=self.theme_colors["bg"], fg=self.get_text_fg(self.theme_colors["bg"]))
            self.track_info_label.configure(bg=self.theme_colors["bg"], fg=self.get_text_fg(self.theme_colors["bg"]))
            self.volume_frame.winfo_children()[0].configure(bg=self.theme_colors["volume_frame_bg"], fg=self.get_text_fg(self.theme_colors["volume_frame_bg"]))
            self.progress_scale.configure(
                bg=self.theme_colors["scale_bg"],
                fg=self.get_text_fg(self.theme_colors["scale_bg"]),
                troughcolor=self.theme_colors["trough"]
            )
            self.volume_scale.configure(
                bg=self.theme_colors["scale_bg"],
                fg=self.get_text_fg(self.theme_colors["scale_bg"]),
                troughcolor=self.theme_colors["trough"]
            )
            if self.notification and self.notification.winfo_exists():
                self.notification.configure(
                    bg="#f5f5f5",
                    fg="#333333"
                )
            for btn in self.buttons.values():
                if btn.winfo_exists():
                    state = btn.cget("state")
                    btn.configure(
                        bg=self.theme_colors["button"] if state == "normal" else self.theme_colors["disabled"],
                        fg=self.get_text_fg(self.theme_colors["button"] if state == "normal" else self.theme_colors["disabled"]),
                        activebackground=self.theme_colors["button_hover"],
                        activeforeground=self.get_text_fg(self.theme_colors["button_hover"])
                    )
        except Exception as e:
            self.log_debug(f"Errore applicazione colori: {str(e)}")
            if self.status_label.winfo_exists():
                self.status_label.config(text="Errore aggiornamento colori")

    def toggle_rgb_mode(self):
        self.is_rgb_mode = not self.is_rgb_mode
        self.rgb_button.configure(
            bg=self.theme_colors["disabled"] if self.is_rgb_mode else self.theme_colors["button"],
            fg=self.get_text_fg(self.theme_colors["disabled"] if self.is_rgb_mode else self.theme_colors["button"])
        )
        if self.is_rgb_mode:
            self.change_colors_rgb()
            self.show_notification("Modalità RGB attivata")
            self.log_debug("Modalità RGB attivata")
        else:
            self.theme_colors = self.default_colors.copy()
            self.current_rgb = {key: self.hex_to_rgb(self.theme_colors[key]) for key in self.theme_colors}
            self.target_rgb = self.current_rgb.copy()
            self.apply_colors()
            if self.rgb_timer:
                try:
                    self.root.after_cancel(self.rgb_timer)
                except tk.TclError:
                    pass
                self.rgb_timer = None
            self.show_notification("Modalità RGB disattivata")
            self.log_debug("Modalità RGB disattivata")
        self.save_config()
        self.reset_idle_timer()

    def toggle_shuffle(self):
        self.is_shuffling = not self.is_shuffling
        self.shuffle_history = []
        self.shuffle_button.configure(
            bg=self.theme_colors["disabled"] if self.is_shuffling else self.theme_colors["button"],
            fg=self.get_text_fg(self.theme_colors["disabled"] if self.is_shuffling else self.theme_colors["button"])
        )
        self.show_notification("Shuffle " + ("attivato" if self.is_shuffling else "disattivato"))
        self.log_debug(f"Shuffle: {self.is_shuffling}")
        self.save_config()
        self.reset_idle_timer()

    def show_startup_message(self):
        self.show_notification("Benvenuto nel lettore musicale, buon ascolto :-)")

    def show_notification(self, message):
        if not self.ui_initialized or not self.root.winfo_exists():
            self.log_debug("Tentativo di mostrare notifica prima dell'inizializzazione UI o dopo chiusura")
            return
        if self.notification and self.notification.winfo_exists():
            self.notification_queue.append(message)
            return
        if self.notification_timer:
            try:
                self.root.after_cancel(self.notification_timer)
            except tk.TclError:
                pass
            self.notification_timer = None
        try:
            self.main_frame.update_idletasks()  # Forza aggiornamento layout
            self.notification = tk.Label(
                self.main_frame,
                text=message,
                font=self.notification_font,
                bg="#f5f5f5",
                fg="#333333",
                relief="solid",
                borderwidth=2,
                padx=15,
                pady=10,
                wraplength=280
            )
            self.notification.place(
                x=self.main_frame.winfo_width() - 20,
                y=self.main_frame.winfo_height() - 20,
                anchor="se"
            )
            self.notification_timer = self.root.after(5000, self.hide_notification)
        except Exception as e:
            self.log_debug(f"Errore creazione notifica: {str(e)}")
            if self.status_label.winfo_exists():
                self.status_label.config(text="Errore creazione notifica")

    def hide_notification(self):
        if self.notification and self.notification.winfo_exists():
            try:
                self.notification.destroy()
            except tk.TclError:
                pass
            self.notification = None
        if self.notification_queue:
            try:
                self.show_notification(self.notification_queue.pop(0))
            except Exception as e:
                self.log_debug(f"Errore elaborazione coda notifiche: {str(e)}")
        else:
            self.notification_timer = None

    def on_minimize(self, event):
        self.is_minimized = True
        self.log_debug("Finestra minimizzata")
        if self.idle_timer:
            try:
                self.root.after_cancel(self.idle_timer)
            except tk.TclError:
                pass
            self.idle_timer = None

    def on_restore(self, event):
        self.is_minimized = False
        self.log_debug("Finestra ripristinata")
        self.update_notification_position()
        self.start_idle_timer()

    def start_idle_timer(self):
        if self.idle_timer:
            try:
                self.root.after_cancel(self.idle_timer)
            except tk.TclError:
                pass
        if not self.is_minimized:
            self.idle_timer = self.root.after(int(self.idle_timeout * 1000), self.on_idle_timeout)

    def reset_idle_timer(self):
        self.last_interaction = time.time()
        self.start_idle_timer()

    def on_idle_timeout(self):
        if not self.ui_initialized or not self.root.winfo_exists() or self.is_minimized:
            return
        if time.time() - self.last_interaction >= self.idle_timeout:
            if not self.is_rgb_mode:
                self.toggle_rgb_mode()
                self.show_notification("Modalità RGB attivata per inattività")
                self.log_debug("Modalità RGB attivata per inattività")
            else:
                self.show_notification("Inattività rilevata. Premi un tasto per continuare.")
                self.log_debug("Timeout inattività")
        self.start_idle_timer()

    def update_playlist(self):
        if not self.ui_initialized or not self.root.winfo_exists():
            self.log_debug("Tentativo di aggiornare playlist prima dell'inizializzazione UI o dopo chiusura")
            return
        self.playlist = []
        self.playlist_box.delete(0, tk.END)
        self.current_track_index = -1
        self.stop_music()
        if not os.path.exists(self.music_folder) or not os.path.isdir(self.music_folder):
            self.status_label.config(text="Cartella musica non valida")
            self.track_info_label.config(text="Nessun brano")
            self.log_debug(f"Cartella musica non valida: {self.music_folder}")
            messagebox.showwarning("Avviso", f"Cartella musica non valida: {self.music_folder}")
            return
        processed_files = set()
        for file in os.listdir(self.music_folder):
            if file.lower().endswith(('.mp3', '.wav')):
                file_path = os.path.join(self.music_folder, file)
                if file_path not in processed_files and os.path.isfile(file_path):
                    try:
                        # Verifica accesso al file
                        with open(file_path, "rb") as f:
                            pass
                        pygame.mixer.music.load(file_path)
                        pygame.mixer.music.unload()
                        self.playlist.append(file_path)
                        display, _, _, _ = self.get_track_info(len(self.playlist) - 1)
                        self.playlist_box.insert(tk.END, display)
                        processed_files.add(file_path)
                    except (pygame.error, IOError, OSError) as e:
                        self.status_label.config(text=f"Errore: {os.path.splitext(file)[0]} non valido")
                        self.log_debug(f"Errore caricamento {file}: {str(e)}")
                        messagebox.showerror("Errore", f"Impossibile caricare {os.path.splitext(file)[0]}: file non valido o corrotto")
        if self.playlist:
            try:
                self.load_metadata_async()
                self.current_track_index = 0
                self.status_label.config(text="Playlist caricata")
                self.update_status_label()
                self.highlight_current_track()
                self.log_debug(f"Playlist caricata: {len(self.playlist)} brani")
            except Exception as e:
                self.log_debug(f"Errore post-caricamento playlist: {str(e)}")
                self.status_label.config(text="Errore aggiornamento playlist")
                messagebox.showerror("Errore", f"Impossibile aggiornare la playlist: {str(e)}")
        else:
            self.status_label.config(text="Nessun brano nella cartella")
            self.track_info_label.config(text="Nessun brano")
            self.log_debug("Nessun brano trovato nella cartella")

    def highlight_current_track(self):
        if not self.ui_initialized or not self.root.winfo_exists():
            return
        try:
            self.playlist_box.selection_clear(0, tk.END)
            if 0 <= self.current_track_index < len(self.playlist):
                self.playlist_box.selection_set(self.current_track_index)
                self.playlist_box.see(self.current_track_index)
        except Exception as e:
            self.log_debug(f"Errore evidenziazione brano corrente: {str(e)}")

    def get_track_info(self, index):
        if index < 0 or index >= len(self.playlist):
            return "Nessun brano", "Sconosciuto", "Sconosciuto", 0
        path = self.playlist[index]
        if path in self.metadata_cache:
            try:
                current_mtime = os.path.getmtime(path)
                if self.metadata_cache[path].get("timestamp", 0) >= current_mtime:
                    return (self.metadata_cache[path]["display"],
                            self.metadata_cache[path].get("artist", "Sconosciuto"),
                            self.metadata_cache[path].get("title", os.path.splitext(os.path.basename(path))[0]),
                            self.metadata_cache[path]["duration"])
            except (OSError, IOError) as e:
                self.log_debug(f"Errore accesso file {path} in get_track_info: {str(e)}")
        try:
            if MUTAGEN_AVAILABLE and path.lower().endswith((".mp3", ".wav")):
                audio = MP3(path) if path.lower().endswith(".mp3") else WAVE(path)
                artist = audio.get("TPE1", ["Sconosciuto"])[0]
                title = audio.get("TIT2", [os.path.splitext(os.path.basename(path))[0]])[0]
                duration = audio.info.length
                display = f"{artist} - {title}" if artist != "Sconosciuto" else title
                self.metadata_cache[path] = {
                    "display": display,
                    "artist": artist,
                    "title": title,
                    "duration": duration,
                    "timestamp": os.path.getmtime(path)
                }
            else:
                display = os.path.splitext(os.path.basename(path))[0]
                self.metadata_cache[path] = {
                    "display": display,
                    "artist": "Sconosciuto",
                    "title": display,
                    "duration": 0,
                    "timestamp": os.path.getmtime(path)
                }
            return display, self.metadata_cache[path]["artist"], self.metadata_cache[path]["title"], self.metadata_cache[path]["duration"]
        except (OSError, IOError, Exception) as e:
            self.log_debug(f"Errore caricamento metadati {path}: {str(e)}")
            display = os.path.splitext(os.path.basename(path))[0]
            self.metadata_cache[path] = {
                "display": display,
                "artist": "Sconosciuto",
                "title": display,
                "duration": 0,
                "timestamp": 0
            }
            return display, "Sconosciuto", display, 0

    def load_metadata_async(self):
        def load():
            processed_files = set()
            for path in self.playlist:
                if path in processed_files:
                    continue
                try:
                    current_mtime = os.path.getmtime(path)
                    if path in self.metadata_cache and self.metadata_cache[path].get("timestamp", 0) >= current_mtime:
                        continue
                except (OSError, IOError) as e:
                    self.log_debug(f"Errore accesso file {path} in load_metadata_async: {str(e)}")
                    continue
                try:
                    if MUTAGEN_AVAILABLE and path.lower().endswith((".mp3", ".wav")):
                        audio = MP3(path) if path.lower().endswith(".mp3") else WAVE(path)
                        artist = audio.get("TPE1", ["Sconosciuto"])[0]
                        title = audio.get("TIT2", [os.path.splitext(os.path.basename(path))[0]])[0]
                        duration = audio.info.length
                        display = f"{artist} - {title}" if artist != "Sconosciuto" else title
                        self.metadata_cache[path] = {
                            "display": display,
                            "artist": artist,
                            "title": title,
                            "duration": duration,
                            "timestamp": current_mtime
                        }
                    else:
                        display = os.path.splitext(os.path.basename(path))[0]
                        self.metadata_cache[path] = {
                            "display": display,
                            "artist": "Sconosciuto",
                            "title": display,
                            "duration": 0,
                            "timestamp": current_mtime
                        }
                    self.metadata_queue.put("update_playlist")
                    processed_files.add(path)
                except (OSError, IOError, Exception) as e:
                    self.log_debug(f"Errore caricamento metadati {path}: {str(e)}")
                    self.metadata_cache[path] = {
                        "display": os.path.splitext(os.path.basename(path))[0],
                        "artist": "Sconosciuto",
                        "title": os.path.splitext(os.path.basename(path))[0],
                        "duration": 0,
                        "timestamp": 0
                    }
                    self.metadata_queue.put("update_playlist")
            self.metadata_queue.put("update_status")
        threading.Thread(target=load, daemon=True).start()

    def check_metadata_queue(self):
        if not self.ui_initialized or not self.root.winfo_exists():
            return
        try:
            while True:
                task = self.metadata_queue.get_nowait()
                if task == "update_playlist" and self.ui_initialized and self.root.winfo_exists():
                    self.playlist_box.delete(0, tk.END)
                    for path in self.playlist:
                        display, _, _, _ = self.get_track_info(self.playlist.index(path))
                        self.playlist_box.insert(tk.END, display)
                    self.highlight_current_track()
                elif task == "update_status" and self.ui_initialized and self.root.winfo_exists():
                    self.update_status_label()
        except queue.Empty:
            pass
        except Exception as e:
            self.log_debug(f"Errore elaborazione coda metadati: {str(e)}")
            if self.status_label.winfo_exists():
                self.status_label.config(text="Errore aggiornamento playlist")
        self.root.after(200, self.check_metadata_queue)

    def update_status_label(self):
        if not self.ui_initialized or not self.root.winfo_exists():
            return
        try:
            if self.current_track_index >= 0 and self.current_track_index < len(self.playlist):
                display, artist, title, duration = self.get_track_info(self.current_track_index)
                status = f"Riproducendo: {display}" if self.is_playing and not self.is_paused else f"In pausa: {display}" if self.is_paused else "Nessun brano selezionato"
                self.status_label.config(text=status)
                self.track_info_label.config(text=display)
            else:
                self.status_label.config(text="Nessun brano nella playlist")
                self.track_info_label.config(text="Nessun brano")
        except Exception as e:
            self.log_debug(f"Errore aggiornamento etichette stato: {str(e)}")
            if self.status_label.winfo_exists():
                self.status_label.config(text="Errore aggiornamento stato")
            if self.track_info_label.winfo_exists():
                self.track_info_label.config(text="Nessun brano")

    def get_track_duration(self):
        if not MUTAGEN_AVAILABLE or self.current_track_index < 0 or self.current_track_index >= len(self.playlist):
            return 0
        path = self.playlist[self.current_track_index]
        if path in self.metadata_cache and self.metadata_cache[path]["duration"] > 0:
            return self.metadata_cache[path]["duration"]
        try:
            audio = MP3(path) if path.lower().endswith(".mp3") else WAVE(path)
            duration = audio.info.length
            self.metadata_cache[path]["duration"] = duration
            self.metadata_cache[path]["timestamp"] = os.path.getmtime(path)
            return duration
        except (OSError, IOError, Exception) as e:
            self.log_debug(f"Errore lettura durata {path}: {str(e)}")
            return 0

    def update_progress(self):
        if not self.ui_initialized or not self.root.winfo_exists():
            return
        if not self.is_playing or self.is_paused or self.is_seeking or self.current_track_index < 0 or self.current_track_index >= len(self.playlist):
            self.root.after(50, self.update_progress)
            return
        current_time = time.time()
        if current_time - self.last_frame_time < 1.0 / self.fps_target:
            self.root.after(10, self.update_progress)
            return
        self.last_frame_time = current_time
        try:
            self.current_time = time.time() - self.start_time
            if self.total_duration > 0 and (not pygame.mixer.music.get_busy() or self.current_time >= self.total_duration):
                if self.is_single_loop:
                    self.stop_music()
                    self.play_music()
                elif self.is_looping and self.current_track_index >= len(self.playlist) - 1:
                    self.current_track_index = 0
                    self.stop_music()
                    self.play_music()
                else:
                    self.next_track()
            else:
                progress = (self.current_time / self.total_duration) * 100 if self.total_duration > 0 else 0
                self.progress_scale.set(min(progress, 100))
                self.time_label.config(text=f"{time.strftime('%M:%S', time.gmtime(self.current_time))} / {time.strftime('%M:%S', time.gmtime(self.total_duration))}")
                self.beat_amplitude = math.sin(time.time() * self.beat_frequency) * self.target_amplitude
                self.apply_beat_effect()
        except pygame.error as e:
            self.stop_music()
            self.status_label.config(text="Errore durante la riproduzione")
            self.track_info_label.config(text="Nessun brano")
            self.log_debug(f"Errore aggiornamento progresso: {str(e)}")
        except Exception as e:
            self.log_debug(f"Errore imprevisto in update_progress: {str(e)}")
            if self.status_label.winfo_exists():
                self.status_label.config(text="Errore aggiornamento progresso")
        self.root.after(50, self.update_progress)

    def apply_beat_effect(self):
        if not self.ui_initialized or not self.root.winfo_exists():
            return
        try:
            amplitude = self.beat_amplitude * 5
            self.controls_frame.configure(pady=int(10 + amplitude))
            if self.is_rgb_mode:
                self.apply_colors()
        except Exception as e:
            self.log_debug(f"Errore applicazione effetto beat: {str(e)}")

    def seek_track_start(self, event):
        if not self.is_playing or not self.total_duration or not MUTAGEN_AVAILABLE or self.current_track_index < 0:
            self.status_label.config(text="Impossibile cercare: brano non valido o metadati mancanti")
            self.log_debug("Seek non possibile: condizioni non soddisfatte")
            return
        self.is_seeking = True
        self.show_seek_label()

    def seek_track(self, event):
        if not self.is_seeking or not self.total_duration:
            return
        try:
            progress = self.progress_scale.get()
            self.current_time = (progress / 100) * self.total_duration
            self.time_label.config(text=f"{time.strftime('%M:%S', time.gmtime(self.current_time))} / {time.strftime('%M:%S', time.gmtime(self.total_duration))}")
            self.update_seek_label()
        except Exception as e:
            self.log_debug(f"Errore durante seek: {str(e)}")

    def seek_track_release(self, event):
        if not self.is_seeking or not self.total_duration:
            self.is_seeking = False
            self.hide_seek_label()
            return
        try:
            progress = self.progress_scale.get()
            seek_time = (progress / 100) * self.total_duration
            self.current_time = seek_time
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            pygame.mixer.music.load(self.playlist[self.current_track_index])
            pygame.mixer.music.play(start=seek_time)
            self.start_time = time.time() - seek_time
            self.is_playing = True
            self.is_paused = False
            display, _, _, _ = self.get_track_info(self.current_track_index)
            self.status_label.config(text=f"Riproducendo: {display}")
            self.track_info_label.config(text=display)
            self.log_debug(f"Seek a {seek_time}s")
        except pygame.error as e:
            self.status_label.config(text="Errore durante il seek")
            self.track_info_label.config(text="Nessun brano")
            self.log_debug(f"Errore seek: {str(e)}")
            messagebox.showerror("Errore", f"Impossibile eseguire il seek: file non valido o corrotto")
            self.stop_music()
        except Exception as e:
            self.log_debug(f"Errore imprevisto in seek_track_release: {str(e)}")
            self.status_label.config(text="Errore durante il seek")
            self.stop_music()
        self.is_seeking = False
        self.hide_seek_label()

    def show_seek_label(self):
        if not self.ui_initialized or not self.root.winfo_exists():
            return
        if self.seek_label and self.seek_label.winfo_exists():
            try:
                self.seek_label.destroy()
            except tk.TclError:
                pass
        try:
            self.seek_label = tk.Label(self.progress_frame, text="Seek in corso...", font=self.label_font, bg=self.theme_colors["progress_frame_bg"], fg=self.get_text_fg(self.theme_colors["progress_frame_bg"]))
            self.seek_label.pack()
        except Exception as e:
            self.log_debug(f"Errore creazione etichetta seek: {str(e)}")

    def update_seek_label(self):
        if self.seek_label and self.seek_label.winfo_exists():
            try:
                self.seek_label.config(text=f"Seek: {time.strftime('%M:%S', time.gmtime(self.current_time))}")
            except Exception as e:
                self.log_debug(f"Errore aggiornamento etichetta seek: {str(e)}")

    def hide_seek_label(self):
        if self.seek_label and self.seek_label.winfo_exists():
            try:
                self.seek_label.destroy()
            except tk.TclError:
                pass
            self.seek_label = None

    def set_volume(self, event=None):
        if not self.ui_initialized or not hasattr(self, 'volume_scale') or not self.root.winfo_exists():
            self.log_debug("Tentativo di impostare volume prima dell'inizializzazione UI o dopo chiusura")
            return
        try:
            volume = self.volume_scale.get() / 100
            pygame.mixer.music.set_volume(volume)
            if self.status_label.winfo_exists():
                self.status_label.config(text=f"Volume impostato al {int(volume*100)}%")
            self.log_debug(f"Volume impostato: {volume}")
            self.save_config()
        except pygame.error as e:
            self.log_debug(f"Errore impostazione volume: {str(e)}")
            if self.status_label.winfo_exists():
                self.status_label.config(text="Errore regolazione volume")
            messagebox.showerror("Errore", f"Impossibile regolare il volume: {str(e)}")
        except Exception as e:
            self.log_debug(f"Errore imprevisto in set_volume: {str(e)}")
            if self.status_label.winfo_exists():
                self.status_label.config(text="Errore regolazione volume")
        self.reset_idle_timer()

    def add_track(self):
        if not self.ui_initialized or not self.root.winfo_exists():
            return
        try:
            files = filedialog.askopenfilenames(filetypes=[("Audio Files", "*.mp3 *.wav")])
            added = 0
            for file in files:
                if file.lower().endswith(('.mp3', '.wav')) and file not in self.playlist:
                    try:
                        with open(file, "rb") as f:
                            pass
                        pygame.mixer.music.load(file)
                        pygame.mixer.music.unload()
                        if MUTAGEN_AVAILABLE:
                            audio = MP3(file) if file.lower().endswith(".mp3") else WAVE(file)
                            if audio.info.length <= 0:
                                raise ValueError("Durata del file non valida")
                        self.playlist.append(file)
                        display, _, _, _ = self.get_track_info(len(self.playlist) - 1)
                        self.playlist_box.insert(tk.END, display)
                        added += 1
                    except (pygame.error, IOError, OSError, ValueError) as e:
                        self.status_label.config(text=f"Errore: {os.path.splitext(os.path.basename(file))[0]} non valido")
                        self.log_debug(f"Errore aggiunta brano {file}: {str(e)}")
                        messagebox.showerror("Errore", f"Impossibile aggiungere {os.path.splitext(os.path.basename(file))[0]}: file non valido o corrotto")
            if added:
                if self.current_track_index == -1 and self.playlist:
                    self.current_track_index = 0
                    self.highlight_current_track()
                    self.update_status_label()
                if len(self.playlist) > 60:
                    messagebox.showwarning("Attenzione", "La playlist contiene più di 60 brani, potrebbe rallentare le prestazioni.")
                    self.log_debug("Playlist supera 60 brani")
                self.show_notification(f"Aggiunti {added} brani alla playlist!")
                self.log_debug(f"Aggiunti {added} brani")
            elif files:
                self.status_label.config(text="Nessun brano valido aggiunto")
        except Exception as e:
            self.log_debug(f"Errore imprevisto in add_track: {str(e)}")
            self.status_label.config(text="Errore aggiunta brani")
            messagebox.showerror("Errore", f"Impossibile aggiungere brani: {str(e)}")
        self.reset_idle_timer()

    def remove_track(self):
        if not self.ui_initialized or not self.root.winfo_exists():
            return
        if not self.playlist_box.curselection():
            self.status_label.config(text="Seleziona un brano da rimuovere")
            self.log_debug("Tentativo di rimozione senza selezione")
            return
        try:
            index = self.playlist_box.curselection()[0]
            if index >= len(self.playlist):
                return
            track_name = os.path.splitext(os.path.basename(self.playlist[index]))[0]
            if index <= self.current_track_index and self.current_track_index > 0:
                self.current_track_index -= 1
            elif index == self.current_track_index:
                self.stop_music()
                self.current_track_index = min(self.current_track_index, len(self.playlist) - 2) if self.playlist else -1
            self.playlist_box.delete(index)
            if self.playlist[index] in self.metadata_cache:
                del self.metadata_cache[self.playlist[index]]
            self.playlist.pop(index)
            if not self.playlist:
                self.current_track_index = -1
                self.shuffle_history = []
                self.status_label.config(text="Nessun brano nella playlist")
                self.track_info_label.config(text="Nessun brano")
            else:
                self.status_label.config(text=f"Rimosso: {track_name}")
                self.update_status_label()
            self.highlight_current_track()
            self.log_debug(f"Brano rimosso: {track_name}")
        except Exception as e:
            self.log_debug(f"Errore rimozione brano: {str(e)}")
            self.status_label.config(text="Errore durante la rimozione del brano")
            messagebox.showerror("Errore", f"Impossibile rimuovere il brano: {str(e)}")
        self.reset_idle_timer()

    def play_selected_track(self, event):
        if not self.ui_initialized or not self.root.winfo_exists():
            return
        if not self.playlist_box.curselection():
            return
        try:
            self.current_track_index = self.playlist_box.curselection()[0]
            if self.current_track_index >= len(self.playlist):
                self.current_track_index = 0
            self.stop_music()
            self.play_music()
        except Exception as e:
            self.log_debug(f"Errore riproduzione brano selezionato: {str(e)}")
            self.status_label.config(text="Errore durante la riproduzione")
            self.track_info_label.config(text="Nessun brano")
            messagebox.showerror("Errore", f"Impossibile riprodurre il brano: {str(e)}")
        self.reset_idle_timer()

    def play_music(self):
        if not self.ui_initialized or not self.root.winfo_exists():
            return
        if not self.playlist or self.current_track_index < 0 or self.current_track_index >= len(self.playlist):
            self.status_label.config(text="Nessun brano valido nella playlist")
            self.track_info_label.config(text="Nessun brano")
            self.log_debug("Tentativo di riproduzione con playlist vuota o indice non valido")
            return
        try:
            with open(self.playlist[self.current_track_index], "rb") as f:
                pass
            pygame.mixer.music.load(self.playlist[self.current_track_index])
            start_time = self.current_time if self.is_paused else 0
            pygame.mixer.music.play(start=start_time)
            self.is_playing = True
            self.is_paused = False
            self.seek_supported = MUTAGEN_AVAILABLE and self.get_track_duration() > 0
            if not self.seek_supported:
                self.progress_scale.config(state="disabled")
            else:
                self.progress_scale.config(state="normal")
            self.start_time = time.time() - start_time
            self.amplitude_transition_start = time.time()
            self.total_duration = self.get_track_duration() if MUTAGEN_AVAILABLE else 0
            if self.total_duration > 0:
                self.beat_frequency = max(0.7, min(2.2, 96 / self.total_duration))
            else:
                self.beat_frequency = random.uniform(0.7, 2.2)
            display, artist, title, duration = self.get_track_info(self.current_track_index)
            self.status_label.config(text=f"Riproducendo: {display}")
            self.track_info_label.config(text=display)
            self.play_button.config(state="disabled", bg=self.theme_colors["disabled"], fg=self.get_text_fg(self.theme_colors["disabled"]))
            self.pause_button.config(state="normal", bg=self.theme_colors["button"], fg=self.get_text_fg(self.theme_colors["button"]))
            self.set_volume()
            self.highlight_current_track()
            self.shuffle_history.append(self.current_track_index)
            current = time.strftime("%M:%S", time.gmtime(self.current_time))
            total = time.strftime("%M:%S", time.gmtime(duration))
            notification_text = f"Ora in riproduzione:\n{artist} - {title}\nDurata: {current} / {total}"
            self.show_notification(notification_text)
            self.log_debug(f"Riproduzione avviata: {display}, beat_frequency: {self.beat_frequency}, durata: {self.total_duration}s, start_time: {start_time}s")
            self.root.after(50, self.update_progress)
        except (pygame.error, IOError, OSError) as e:
            self.status_label.config(text="Errore riproduzione: file non valido")
            self.track_info_label.config(text="Nessun brano")
            self.log_debug(f"Errore riproduzione brano {self.playlist[self.current_track_index]}: {str(e)}")
            messagebox.showerror("Errore", f"Impossibile riprodurre {os.path.splitext(os.path.basename(self.playlist[self.current_track_index]))[0]}: file non valido o corrotto")
            self.stop_music()
        except Exception as e:
            self.log_debug(f"Errore imprevisto in play_music: {str(e)}")
            self.status_label.config(text="Errore riproduzione")
            self.track_info_label.config(text="Nessun brano")
            self.stop_music()
        self.reset_idle_timer()

    def pause_music(self):
        if not self.ui_initialized or not self.root.winfo_exists():
            return
        if not self.is_playing or self.current_track_index < 0 or self.current_track_index >= len(self.playlist):
            return
        try:
            if not self.is_paused:
                self.current_time = time.time() - self.start_time
                pygame.mixer.music.stop()
                self.is_paused = True
                self.is_playing = False
                self.amplitude_transition_start = time.time()
                display, _, _, _ = self.get_track_info(self.current_track_index)
                self.status_label.config(text=f"In pausa: {display}")
                self.track_info_label.config(text=display)
                self.play_button.config(state="normal", bg=self.theme_colors["button"], fg=self.get_text_fg(self.theme_colors["button"]))
                self.pause_button.config(state="disabled", bg=self.theme_colors["disabled"], fg=self.get_text_fg(self.theme_colors["disabled"]))
                self.log_debug(f"Musica in pausa a {self.current_time}s")
            else:
                self.play_music()
                self.log_debug("Ripresa riproduzione")
        except pygame.error as e:
            self.status_label.config(text="Errore durante la pausa/ripresa")
            self.track_info_label.config(text="Nessun brano")
            self.log_debug(f"Errore pausa/ripresa: {str(e)}")
            messagebox.showerror("Errore", f"Impossibile mettere in pausa/riprendere: {str(e)}")
            self.stop_music()
        except Exception as e:
            self.log_debug(f"Errore imprevisto in pause_music: {str(e)}")
            self.status_label.config(text="Errore durante la pausa/ripresa")
            self.stop_music()
        self.reset_idle_timer()

    def stop_music(self):
        if not self.ui_initialized or not self.root.winfo_exists():
            return
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            self.is_playing = False
            self.is_paused = False
            self.is_seeking = False
            self.current_time = 0
            if self.progress_scale.winfo_exists():
                self.progress_scale.set(0)
            if self.time_label.winfo_exists():
                self.time_label.config(text="00:00 / 00:00")
            if self.play_button.winfo_exists():
                self.play_button.config(state="normal", bg=self.theme_colors["button"], fg=self.get_text_fg(self.theme_colors["button"]))
            if self.pause_button.winfo_exists():
                self.pause_button.config(state="disabled", bg=self.theme_colors["disabled"], fg=self.get_text_fg(self.theme_colors["disabled"]))
            if self.current_track_index >= 0 and self.current_track_index < len(self.playlist):
                display, _, _, _ = self.get_track_info(self.current_track_index)
                self.status_label.config(text=f"Fermato: {display}")
                self.track_info_label.config(text=display)
            else:
                self.status_label.config(text="Nessun brano")
                self.track_info_label.config(text="Nessun brano")
            self.amplitude_transition_start = time.time()
            self.hide_seek_label()
            self.log_debug("Musica fermata")
        except pygame.error as e:
            self.log_debug(f"Errore stop musica: {str(e)}")
            if self.status_label.winfo_exists():
                self.status_label.config(text="Errore durante l'arresto")
            if self.track_info_label.winfo_exists():
                self.track_info_label.config(text="Nessun brano")
            messagebox.showerror("Errore", f"Impossibile arrestare la musica: {str(e)}")
        except Exception as e:
            self.log_debug(f"Errore imprevisto in stop_music: {str(e)}")
            if self.status_label.winfo_exists():
                self.status_label.config(text="Errore durante l'arresto")
        self.reset_idle_timer()

    def prev_track(self):
        if not self.ui_initialized or not self.root.winfo_exists():
            return
        if not self.playlist or self.current_track_index < 0 or self.current_track_index >= len(self.playlist):
            self.status_label.config(text="Nessun brano precedente")
            self.track_info_label.config(text="Nessun brano")
            self.log_debug("Tentativo di passare al brano precedente con playlist vuota o indice non valido")
            return
        try:
            if self.is_shuffling and self.shuffle_history:
                self.shuffle_history.pop()
                self.current_track_index = self.shuffle_history[-1] if self.shuffle_history else max(0, self.current_track_index - 1)
            else:
                self.current_track_index = max(0, self.current_track_index - 1)
            self.stop_music()
            self.play_music()
            display, _, _, _ = self.get_track_info(self.current_track_index)
            self.show_notification(f"Brano precedente: {display}")
            self.log_debug(f"Brano precedente: {self.current_track_index}")
        except Exception as e:
            self.log_debug(f"Errore passaggio a brano precedente: {str(e)}")
            self.status_label.config(text="Errore passaggio a brano precedente")
            self.track_info_label.config(text="Nessun brano")
            messagebox.showerror("Errore", f"Impossibile passare al brano precedente: {str(e)}")
        self.reset_idle_timer()

    def next_track(self):
        if not self.ui_initialized or not self.root.winfo_exists():
            return
        if not self.playlist or self.current_track_index < 0 or self.current_track_index >= len(self.playlist):
            self.status_label.config(text="Nessun brano successivo")
            self.track_info_label.config(text="Nessun brano")
            self.log_debug("Tentativo di passare al brano successivo con playlist vuota o indice non valido")
            return
        try:
            if self.is_shuffling:
                available_indices = [i for i in range(len(self.playlist)) if i not in self.shuffle_history[-10:]]
                if not available_indices:
                    self.shuffle_history = self.shuffle_history[-1:]
                    available_indices = list(range(len(self.playlist)))
                self.current_track_index = random.choice(available_indices)
            else:
                self.current_track_index += 1
                if self.current_track_index >= len(self.playlist):
                    self.current_track_index = 0 if self.is_looping else -1
            if self.current_track_index >= 0:
                self.stop_music()
                self.play_music()
                display, _, _, _ = self.get_track_info(self.current_track_index)
                self.show_notification(f"Brano successivo: {display}")
                self.log_debug(f"Brano successivo: {self.current_track_index}")
            else:
                self.stop_music()
        except Exception as e:
            self.log_debug(f"Errore passaggio a brano successivo: {str(e)}")
            self.status_label.config(text="Errore passaggio a brano successivo")
            self.track_info_label.config(text="Nessun brano")
            messagebox.showerror("Errore", f"Impossibile passare al brano successivo: {str(e)}")
        self.reset_idle_timer()

if __name__ == "__main__":
    root = tk.Tk()
    try:
        app = MusicPlayer(root)
        root.mainloop()
    except Exception as e:
        print(f"Errore esecuzione mainloop: {str(e)}")
import os
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pygame
import sys

try:
    from mutagen.mp3 import MP3
    from mutagen.wave import WAVE
except ImportError:
    print("La librería 'mutagen' no está instalada. Instálala con: pip install mutagen")
    sys.exit(1)

class NOVAPlayerApp:
    """
    Una aplicación de reproductor de música con Tkinter y Pygame.
    Soporta archivos .mp3 y .wav, con barra de progreso manipulable y control de volumen.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("🎵 Nuba Player")

        icon_path = "enriquee.ico"
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception as e:
                print(f"[Advertencia] No se pudo asignar el icono: {e}")
        else:
            print(f"[Advertencia] El icono no fue encontrado: {icon_path}")

        self.root.geometry("500x550")
        self.root.configure(bg="#121212")
        self.root.resizable(False, False)

        # Estado
        self.current_folder = ""
        self.playing = False
        self.paused = False
        self.selected_file = ""
        self.song_length = 0
        self.start_offset = 0
        self.progress_job = None
        self.is_seeking = False

        pygame.mixer.init()
        self.setup_styles()
        self.create_widgets()

    def setup_styles(self):
        style = ttk.Style(self.root)
        style.theme_use('clam')

        style.configure("TButton",
            background="#1f1f1f",
            foreground="white",
            font=("Helvetica", 12),
            relief="flat",
            borderwidth=0,
            padding=8)
        style.map("TButton",
            background=[('active', '#333333')])

        style.configure("Play.TButton", background="#1db954", font=("Helvetica", 12, "bold"))
        style.map("Play.TButton", background=[('active', '#1ed760')])

        style.configure("Stop.TButton", background="#f44336")
        style.map("Stop.TButton", background=[('active', '#e57373')])

        style.configure("green.Horizontal.TProgressbar", troughcolor='#1f1f1f', background='#1db954', bordercolor="#1f1f1f", lightcolor='#1db954', darkcolor='#1db954')
        style.configure("Horizontal.TScale", troughcolor='#1f1f1f', background='#1db954')

    def create_widgets(self):
        self.label = tk.Label(self.root, text="Selecciona una carpeta con MP3 o WAV", fg="white", bg="#121212", font=("Helvetica", 14))
        self.label.pack(pady=10)

        self.choose_button = ttk.Button(self.root, text="📂 Elegir Carpeta", command=self.choose_folder)
        self.choose_button.pack(pady=5)
        
        list_frame = tk.Frame(self.root, bg="#333333", bd=1)
        list_frame.pack(pady=10, padx=20)
        self.song_list = tk.Listbox(list_frame, bg="#1f1f1f", fg="white", selectbackground="#333", font=("Helvetica", 12), width=60, height=10, relief=tk.FLAT, borderwidth=0, highlightthickness=0)
        self.song_list.pack()
        self.song_list.bind("<<ListboxSelect>>", self.on_select)

        progress_frame = tk.Frame(self.root, bg="#121212")
        progress_frame.pack(pady=5, padx=20, fill='x')

        self.time_label = tk.Label(progress_frame, text="00:00 / 00:00", fg="white", bg="#121212", font=("Helvetica", 10))
        self.time_label.pack(side='left')

        self.progress_bar = ttk.Progressbar(progress_frame, orient='horizontal', mode='determinate', style="green.Horizontal.TProgressbar")
        self.progress_bar.pack(side='right', fill='x', expand=True, padx=(10,0))
        self.progress_bar.bind("<Button-1>", self.start_seek)
        self.progress_bar.bind("<B1-Motion>", self.update_seek)
        self.progress_bar.bind("<ButtonRelease-1>", self.end_seek)

        control_frame = tk.Frame(self.root, bg="#121212")
        control_frame.pack(pady=10)

        self.play_button = ttk.Button(control_frame, text="▶️ Reproducir", command=self.play_song, style="Play.TButton")
        self.play_button.pack(side='left', padx=10)

        self.pause_button = ttk.Button(control_frame, text="⏸ Pausar", command=self.toggle_pause)
        self.pause_button.pack(side='left', padx=10)

        self.stop_button = ttk.Button(control_frame, text="⏹️ Detener", command=self.stop_song, style="Stop.TButton")
        self.stop_button.pack(side='left', padx=10)

        volume_frame = tk.Frame(self.root, bg="#121212")
        volume_frame.pack(pady=10, padx=20, fill='x')
        
        volume_label = tk.Label(volume_frame, text="🔊", fg="white", bg="#121212", font=("Helvetica", 12))
        volume_label.pack(side='left')

        self.volume_slider = ttk.Scale(volume_frame, from_=0, to=1, orient='horizontal', command=self.set_volume, style="Horizontal.TScale")
        self.volume_slider.set(0.7)
        self.volume_slider.pack(side='right', fill='x', expand=True, padx=(10,0))

    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.stop_song()
            self.current_folder = folder
            self.song_list.delete(0, tk.END)
            try:
                for file in os.listdir(folder):
                    if file.lower().endswith((".mp3", ".wav")):
                        self.song_list.insert(tk.END, file)
                self.label.config(text=f"Carpeta: {os.path.basename(folder)}")
            except OSError as e:
                messagebox.showerror("Error de Lectura", f"No se pudo leer la carpeta:\n{e}")

    def on_select(self, event):
        if not self.song_list.curselection():
            return
        self.stop_song()
        self.selected_file = self.song_list.get(self.song_list.curselection())
        self.get_song_info()

    def get_song_info(self):
        if not self.selected_file: return
        full_path = os.path.join(self.current_folder, self.selected_file)
        try:
            if full_path.lower().endswith(".mp3"): audio = MP3(full_path)
            elif full_path.lower().endswith(".wav"): audio = WAVE(full_path)
            else: return
            self.song_length = int(audio.info.length)
            self.progress_bar['maximum'] = self.song_length
            total_minutes, total_seconds = divmod(self.song_length, 60)
            self.time_label.config(text=f"00:00 / {total_minutes:02d}:{total_seconds:02d}")
            self.progress_bar['value'] = 0
        except Exception as e:
            messagebox.showerror("Error de Metadatos", f"No se pudo leer la información del archivo:\n{self.selected_file}\n\nError: {e}")
            self.time_label.config(text="Error")
            self.song_length = 0

    def play_song(self):
        if not self.selected_file:
            messagebox.showwarning("Advertencia", "Selecciona una canción primero.")
            return
        self.start_offset = 0
        full_path = os.path.join(self.current_folder, self.selected_file)
        try:
            pygame.mixer.music.load(full_path)
            pygame.mixer.music.play()
            self.playing = True
            self.paused = False
            self.pause_button.config(text="⏸ Pausar")
            self.update_progress()
        except pygame.error as e:
            messagebox.showerror("Error de Reproducción", f"No se pudo reproducir el archivo:\n{self.selected_file}\n\nError: {e}")
            self.playing = False

    def toggle_pause(self):
        if not self.playing: return
        if self.paused:
            pygame.mixer.music.unpause()
            self.pause_button.config(text="⏸ Pausar")
            self.paused = False
            self.update_progress()
        else:
            pygame.mixer.music.pause()
            self.pause_button.config(text="▶️ Reanudar")
            self.paused = True
            if self.progress_job:
                self.root.after_cancel(self.progress_job)

    def stop_song(self):
        if self.progress_job:
            self.root.after_cancel(self.progress_job)
            self.progress_job = None
        pygame.mixer.music.stop()
        self.playing = False
        self.paused = False
        self.progress_bar['value'] = 0
        self.time_label.config(text="00:00 / 00:00" if not self.selected_file else f"00:00 / {int(self.song_length//60):02d}:{int(self.song_length%60):02d}")
        self.pause_button.config(text="⏸ Pausar")

    def set_volume(self, val):
        pygame.mixer.music.set_volume(float(val))

    def start_seek(self, event):
        if self.song_length > 0:
            self.is_seeking = True
            self.update_seek(event)

    def update_seek(self, event):
        if self.is_seeking:
            clicked_x = event.x
            bar_width = self.progress_bar.winfo_width()
            seek_time = (clicked_x / bar_width) * self.song_length
            seek_time = max(0, min(seek_time, self.song_length))
            self.progress_bar['value'] = seek_time
            total_minutes, total_seconds = divmod(self.song_length, 60)
            current_minutes, current_seconds = divmod(int(seek_time), 60)
            self.time_label.config(text=f"{current_minutes:02d}:{current_seconds:02d} / {total_minutes:02d}:{total_seconds:02d}")

    def end_seek(self, event):
        if not self.is_seeking:
            return
        self.is_seeking = False
        if not self.selected_file or self.song_length == 0:
            return
        clicked_x = event.x
        bar_width = self.progress_bar.winfo_width()
        seek_time = (clicked_x / bar_width) * self.song_length
        seek_time = max(0, min(seek_time, self.song_length))
        self.start_offset = seek_time
        full_path = os.path.join(self.current_folder, self.selected_file)
        pygame.mixer.music.load(full_path)
        pygame.mixer.music.play(start=seek_time)
        self.playing = True
        if self.paused:
            pygame.mixer.music.pause()
        else:
            self.paused = False
            self.pause_button.config(text="⏸ Pausar")
            self.update_progress()

    def update_progress(self):
        if self.is_seeking:
            return
        if self.playing and not self.paused and pygame.mixer.music.get_busy():
            current_time = self.start_offset + (pygame.mixer.music.get_pos() / 1000)
            if current_time >= self.song_length:
                self.stop_song()
                return
            self.progress_bar['value'] = current_time
            total_minutes, total_seconds = divmod(self.song_length, 60)
            current_minutes, current_seconds = divmod(int(current_time), 60)
            self.time_label.config(text=f"{current_minutes:02d}:{current_seconds:02d} / {total_minutes:02d}:{total_seconds:02d}")
            self.progress_job = self.root.after(1000, self.update_progress)
        elif not pygame.mixer.music.get_busy() and self.playing:
            self.stop_song()

if __name__ == "__main__":
    root = tk.Tk()
    app = NOVAPlayerApp(root)
    def on_closing():
        pygame.mixer.quit()
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

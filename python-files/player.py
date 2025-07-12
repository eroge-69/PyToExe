import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import pygame
import os


class MusicPlayer(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Настройка окна приложения
        self.title("Music Player")
        self.geometry("800x400")
        self.resizable(False, False)
        
        # Загрузка иконки приложения
        try:
            icon_path = os.path.join(os.getcwd(), 'icon.ico')
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception as e:
            print(f'Ошибка загрузки иконки: {e}')
            
        # Инициализация PyGame mixer
        pygame.mixer.init()
    
        # Основные элементы управления
        self.create_widgets()
        
        # Текущие настройки
        self.current_theme = 'light'
        self.theme_colors = {
            'light': {'bg': '#ffffff', 'fg': '#333333'},
            'dark': {'bg': '#333333', 'fg': '#ffffff'}
        }
    
    def create_widgets(self):
        # Фреймы
        top_frame = ttk.Frame(self)
        bottom_frame = ttk.Frame(self)
        control_frame = ttk.Frame(bottom_frame)
        
        top_frame.pack(side=tk.TOP, fill=tk.X)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        control_frame.pack(side=tk.LEFT, padx=(20, 0))
        
        # Верхняя панель (логотип и название)
        logo_label = ttk.Label(top_frame, text="Music Player", font=('Segoe UI', 24), anchor='w')
        logo_label.pack(fill=tk.X, pady=(10, 0))
        
        # Панель выбора треков
        playlist_frame = ttk.Frame(bottom_frame)
        playlist_frame.pack(side=tk.RIGHT, fill=tk.Y, expand=True)
        
        # Плейлист
        self.playlist_box = tk.Listbox(playlist_frame, selectmode=tk.SINGLE, height=10, width=50)
        self.playlist_box.pack(padx=10, pady=10)
        
        # Кнопка добавления файлов
        add_button = ttk.Button(control_frame, text="Add Tracks", command=self.add_tracks)
        add_button.pack(pady=10)
        
        # Контроль воспроизведением
        play_button = ttk.Button(control_frame, text="Play", command=self.play_track)
        pause_button = ttk.Button(control_frame, text="Pause", command=self.pause_track)
        stop_button = ttk.Button(control_frame, text="Stop", command=self.stop_track)
        
        play_button.pack(pady=5)
        pause_button.pack(pady=5)
        stop_button.pack(pady=5)
        
        # Переключение тем
        theme_switcher = ttk.Checkbutton(
            top_frame,
            text="Dark Theme",
            variable=tk.BooleanVar(),
            onvalue=True,
            offvalue=False,
            command=self.toggle_theme
        )
        theme_switcher.pack(side=tk.RIGHT, padx=10)
        
    def toggle_theme(self):
        """Переключаем тему"""
        new_theme = 'dark' if self.current_theme == 'light' else 'light'
        colors = self.theme_colors[new_theme]
        for widget in self.winfo_children():
            widget.configure(background=colors['bg'], foreground=colors['fg'])
        self.current_theme = new_theme
    
    def add_tracks(self):
        """Открываем диалоговое окно для выбора музыкальных файлов"""
        tracks = filedialog.askopenfilenames(filetypes=[("MP3 Files", "*.mp3")])
        for track in tracks:
            self.playlist_box.insert(tk.END, os.path.basename(track))
    
    def play_track(self):
        """Воспроизводит выбранный трек"""
        selected = self.playlist_box.curselection()
        if not selected:
            return
        index = int(selected[0])
        filename = self.playlist_box.get(index)
        fullpath = os.path.abspath(filename)
        pygame.mixer.music.load(fullpath)
        pygame.mixer.music.play()
    
    def pause_track(self):
        """Приостанавливает воспроизведение"""
        pygame.mixer.music.pause()
    
    def stop_track(self):
        """Остановливает воспроизведение"""
        pygame.mixer.music.stop()


if __name__ == "__main__":
    app = MusicPlayer()
    app.mainloop()
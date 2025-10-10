#!/usr/bin/env python3
"""
TRACK SWIPE - LECTEUR AUDIO DJ PRO
Design moderne avec égaliseur et icônes élégantes
Version complète avec organisation optimisée
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import os
import shutil
import time
import random

try:
    import vlc
    VLC_OK = True
except ImportError:
    VLC_OK = False

class TrackSwipe:
    def __init__(self, root):
        self.root = root
        self.root.title("🎵 TRACK SWIPE - Lecteur Audio DJ")
        self.root.geometry("1400x950")
        self.root.configure(bg="#0a0e17")
        
        if not VLC_OK:
            messagebox.showerror(
                "VLC requis",
                "Installation requise:\n\n" +
                "1. VLC Media Player: https://www.videolan.org/vlc/\n" +
                "2. Dans cmd: pip install python-vlc\n\n" +
                "Puis relancez le programme."
            )
            self.root.after(100, self.root.destroy)
            return
        
        # Variables
        self.playlist = []
        self.current_index = 0
        self.is_playing = False
        self.delete_folder = "Fichiers_Supprimes"
        self.moved_count = 0
        
        # VLC Player
        self.instance = vlc.Instance('--no-xlib')
        self.player = self.instance.media_player_new()
        self.player.audio_set_volume(70)
        
        # Variables égaliseur
        self.eq_bars = []
        self.eq_heights = [0] * 32
        self.eq_target_heights = [0] * 32
        
        # Palette de couleurs élégante
        self.colors = {
            'bg_dark': '#0a0e17',
            'bg_card': '#161b2e',
            'bg_hover': '#1f2537',
            'accent_primary': '#3b6dff',
            'accent_secondary': '#6b4eff',
            'accent_success': '#00ff66',
            'accent_danger': '#ff0033',
            'text_primary': '#ffffff',
            'text_secondary': '#8b92a8'
        }
        
        self.create_ui()
        self.update_timer()
        self.animate_equalizer()
        
    def create_ui(self):
        # CONTAINER PRINCIPAL
        main_container = tk.Frame(self.root, bg=self.colors['bg_dark'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # HEADER COMPACT
        header_frame = tk.Frame(main_container, bg=self.colors['bg_dark'])
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_canvas = tk.Canvas(
            header_frame,
            height=50,
            bg=self.colors['bg_dark'],
            highlightthickness=0
        )
        title_canvas.pack(fill=tk.X)
        
        title_canvas.create_text(
            700, 25,
            text="TRACK SWIPE",
            font=("Arial", 28, "bold"),
            fill=self.colors['accent_primary']
        )
        
        # Ligne séparation
        separator = tk.Canvas(
            header_frame,
            height=2,
            bg=self.colors['bg_dark'],
            highlightthickness=0
        )
        separator.pack(fill=tk.X, pady=8)
        separator.create_line(0, 1, 1400, 1, fill=self.colors['accent_primary'], width=2)
        
        # COLONNES
        content_frame = tk.Frame(main_container, bg=self.colors['bg_dark'])
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # COLONNE GAUCHE - Lecteur principal
        left_frame = tk.Frame(content_frame, bg=self.colors['bg_dark'])
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # COLONNE CENTRE - Tempo et Volume
        center_frame = tk.Frame(content_frame, bg=self.colors['bg_dark'], width=400)
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        center_frame.pack_propagate(False)
        
        # COLONNE DROITE - Playlist
        right_frame = tk.Frame(content_frame, bg=self.colors['bg_card'], width=320)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH)
        right_frame.pack_propagate(False)
        
        # === COLONNE GAUCHE ===
        
        # ÉGALISEUR COMPACT
        eq_container = tk.Frame(left_frame, bg=self.colors['bg_card'], height=130)
        eq_container.pack(fill=tk.X, pady=(0, 15))
        eq_container.pack_propagate(False)
        
        tk.Label(
            eq_container,
            text="🎚️ ÉGALISEUR",
            font=("Arial", 9, "bold"),
            bg=self.colors['bg_card'],
            fg=self.colors['accent_primary']
        ).pack(pady=(8, 3))
        
        self.eq_canvas = tk.Canvas(
            eq_container,
            height=90,
            bg=self.colors['bg_dark'],
            highlightthickness=0
        )
        self.eq_canvas.pack(fill=tk.BOTH, padx=15, pady=(0, 8))
        
        bar_width = 18
        spacing = 4
        for i in range(32):
            x = i * (bar_width + spacing) + 10
            bar = self.eq_canvas.create_rectangle(
                x, 80, x + bar_width, 80,
                fill='', outline=''
            )
            self.eq_bars.append(bar)
        
        # BOUTON CHARGER
        self.btn_load = tk.Button(
            left_frame,
            text="📁 CHARGER FICHIERS",
            command=self.load_files,
            font=("Arial", 11, "bold"),
            bg=self.colors['accent_primary'],
            fg='white',
            activebackground=self.colors['accent_secondary'],
            cursor="hand2",
            relief=tk.FLAT,
            bd=0,
            padx=25,
            pady=12
        )
        self.btn_load.pack(pady=8, fill=tk.X)
        self.add_hover_effect(self.btn_load, self.colors['accent_primary'], self.colors['accent_secondary'])
        
        # DOSSIER COMPACT
        folder_card = tk.Frame(left_frame, bg=self.colors['bg_card'])
        folder_card.pack(pady=8, fill=tk.X)
        
        tk.Label(
            folder_card,
            text="📂 Dossier de suppression",
            bg=self.colors['bg_card'],
            fg=self.colors['text_secondary'],
            font=("Arial", 8)
        ).pack(anchor=tk.W, padx=12, pady=(8, 3))
        
        folder_input = tk.Frame(folder_card, bg=self.colors['bg_card'])
        folder_input.pack(fill=tk.X, padx=12, pady=(0, 8))
        
        self.entry_folder = tk.Entry(
            folder_input,
            font=("Arial", 9),
            bg=self.colors['bg_dark'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['accent_primary'],
            relief=tk.FLAT,
            bd=0
        )
        self.entry_folder.insert(0, self.delete_folder)
        self.entry_folder.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, ipadx=8)
        
        tk.Button(
            folder_input,
            text="📂",
            command=self.select_folder,
            font=("Arial", 10),
            bg=self.colors['bg_hover'],
            fg=self.colors['text_primary'],
            cursor="hand2",
            relief=tk.FLAT,
            padx=12
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        # INFO PISTE COMPACT
        info_card = tk.Frame(left_frame, bg=self.colors['bg_card'])
        info_card.pack(pady=10, fill=tk.X)
        
        self.label_track = tk.Label(
            info_card,
            text="Aucune piste chargée",
            font=("Arial", 11, "bold"),
            bg=self.colors['bg_card'],
            fg=self.colors['text_primary'],
            wraplength=550,
            height=2
        )
        self.label_track.pack(pady=10, padx=12)
        
        self.label_pos = tk.Label(
            info_card,
            text="0 / 0",
            font=("Arial", 8),
            bg=self.colors['bg_card'],
            fg=self.colors['text_secondary']
        )
        self.label_pos.pack(pady=(0, 10))
        
        # TEMPS
        self.label_time = tk.Label(
            left_frame,
            text="0:00 / 0:00",
            font=("Arial", 10, "bold"),
            bg=self.colors['bg_dark'],
            fg=self.colors['accent_primary']
        )
        self.label_time.pack(pady=6)
        
        # BARRE PROGRESSION
        progress_container = tk.Frame(left_frame, bg=self.colors['bg_dark'])
        progress_container.pack(pady=3, fill=tk.X)
        
        self.progress_canvas = tk.Canvas(
            progress_container,
            height=6,
            bg=self.colors['bg_card'],
            highlightthickness=0,
            cursor="hand2"
        )
        self.progress_canvas.pack(fill=tk.X)
        
        self.progress_bar = self.progress_canvas.create_rectangle(
            0, 0, 0, 6,
            fill=self.colors['accent_primary'],
            outline=''
        )
        
        self.progress_canvas.bind("<Button-1>", self.seek_click)
        
        # CONTRÔLES PRINCIPAUX
        controls = tk.Frame(left_frame, bg=self.colors['bg_dark'])
        controls.pack(pady=15)
        
        control_style = {
            'cursor': 'hand2',
            'relief': tk.FLAT,
            'bd': 0,
            'font': ("Arial", 18, "bold")
        }
        
        # Précédent
        self.btn_prev = tk.Button(
            controls,
            text="◄",
            command=self.previous_track,
            bg=self.colors['bg_card'],
            fg=self.colors['text_primary'],
            width=4,
            **control_style
        )
        self.btn_prev.grid(row=0, column=0, padx=6)
        self.add_hover_effect(self.btn_prev, self.colors['bg_card'], self.colors['bg_hover'])
        
        # Play/Pause
        self.btn_play = tk.Button(
            controls,
            text="▶",
            command=self.toggle_play,
            font=("Arial", 24, "bold"),
            bg=self.colors['accent_primary'],
            fg='white',
            width=4,
            cursor='hand2',
            relief=tk.FLAT,
            bd=0
        )
        self.btn_play.grid(row=0, column=1, padx=10)
        self.add_hover_effect(self.btn_play, self.colors['accent_primary'], self.colors['accent_secondary'])
        
        # Suivant
        self.btn_next = tk.Button(
            controls,
            text="▶",
            command=self.next_track,
            bg=self.colors['accent_success'],
            fg='white',
            width=4,
            **control_style
        )
        self.btn_next.grid(row=0, column=2, padx=10)
        self.add_hover_effect(self.btn_next, self.colors['accent_success'], '#00b386')
        
        # Supprimer
        self.btn_delete = tk.Button(
            controls,
            text="✕",
            command=self.delete_and_next,
            bg=self.colors['accent_danger'],
            fg='white',
            width=4,
            **control_style
        )
        self.btn_delete.grid(row=0, column=3, padx=6)
        self.add_hover_effect(self.btn_delete, self.colors['accent_danger'], '#ee3644')
        
        # STATS
        stats_card = tk.Frame(left_frame, bg=self.colors['bg_card'])
        stats_card.pack(pady=8, fill=tk.X)
        
        self.label_stats = tk.Label(
            stats_card,
            text="✓ Fichiers déplacés: 0",
            font=("Arial", 9, "bold"),
            bg=self.colors['bg_card'],
            fg=self.colors['accent_success'],
            pady=10
        )
        self.label_stats.pack()
        
        # === COLONNE CENTRE - TEMPO ET VOLUME ===
        
        # SECTION TEMPO - GRANDE ET VISIBLE
        tempo_card = tk.Frame(center_frame, bg=self.colors['bg_card'], 
                             highlightbackground=self.colors['accent_primary'], 
                             highlightthickness=3)
        tempo_card.pack(pady=(0, 15), fill=tk.BOTH, expand=True)
        
        # Titre tempo
        tempo_header = tk.Label(
            tempo_card,
            text="⚡ CONTRÔLE TEMPO ⚡",
            font=("Arial", 16, "bold"),
            bg=self.colors['bg_card'],
            fg=self.colors['accent_primary']
        )
        tempo_header.pack(pady=(15, 10))
        
        # Container scrollable pour le tempo
        tempo_inner = tk.Frame(tempo_card, bg=self.colors['bg_card'])
        tempo_inner.pack(fill=tk.BOTH, expand=True, padx=15)
        
        # Frame pour le slider et le label
        tempo_frame = tk.Frame(tempo_inner, bg=self.colors['bg_card'])
        tempo_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            tempo_frame,
            text="Vitesse:",
            bg=self.colors['bg_card'],
            fg=self.colors['text_primary'],
            font=("Arial", 11, "bold")
        ).pack(pady=(0, 8))
        
        self.tempo_var = tk.DoubleVar(value=1.0)
        
        # Slider tempo VERTICAL pour gagner de l'espace
        slider_container = tk.Frame(tempo_frame, bg=self.colors['bg_card'])
        slider_container.pack(fill=tk.BOTH, expand=True)
        
        tempo_scale = tk.Scale(
            slider_container,
            from_=2.0,
            to=0.5,
            orient=tk.VERTICAL,
            variable=self.tempo_var,
            command=self.change_tempo,
            bg=self.colors['bg_card'],
            fg=self.colors['text_primary'],
            troughcolor=self.colors['bg_dark'],
            activebackground=self.colors['accent_primary'],
            highlightthickness=0,
            bd=0,
            showvalue=False,
            resolution=0.01,
            sliderrelief=tk.FLAT,
            length=200,
            width=25
        )
        tempo_scale.pack(side=tk.LEFT, padx=(80, 20))
        
        # Label tempo ÉNORME à droite
        self.label_tempo = tk.Label(
            slider_container,
            text="100%",
            bg=self.colors['bg_dark'],
            fg=self.colors['accent_primary'],
            font=("Arial", 28, "bold"),
            width=6,
            relief=tk.FLAT,
            padx=10,
            pady=15
        )
        self.label_tempo.pack(side=tk.LEFT)
        
        # Presets tempo en grille
        preset_frame = tk.Frame(tempo_inner, bg=self.colors['bg_card'])
        preset_frame.pack(pady=15)
        
        tk.Label(
            preset_frame,
            text="Presets rapides:",
            bg=self.colors['bg_card'],
            fg=self.colors['text_secondary'],
            font=("Arial", 9)
        ).pack(pady=(0, 8))
        
        presets_grid = tk.Frame(preset_frame, bg=self.colors['bg_card'])
        presets_grid.pack()
        
        presets = [
            ("50%", 0.5), ("75%", 0.75), ("100%", 1.0),
            ("125%", 1.25), ("150%", 1.5), ("200%", 2.0)
        ]
        
        for idx, (text, value) in enumerate(presets):
            btn = tk.Button(
                presets_grid,
                text=text,
                command=lambda v=value: self.set_tempo_preset(v),
                font=("Arial", 10, "bold"),
                bg=self.colors['bg_dark'],
                fg=self.colors['text_primary'],
                cursor="hand2",
                relief=tk.FLAT,
                padx=12,
                pady=6,
                width=6
            )
            row = idx // 3
            col = idx % 3
            btn.grid(row=row, column=col, padx=3, pady=3)
            self.add_hover_effect(btn, self.colors['bg_dark'], self.colors['bg_hover'])
        
        # SECTION VOLUME
        vol_card = tk.Frame(center_frame, bg=self.colors['bg_card'])
        vol_card.pack(pady=(0, 10), fill=tk.X)
        
        tk.Label(
            vol_card,
            text="🔊 VOLUME",
            font=("Arial", 12, "bold"),
            bg=self.colors['bg_card'],
            fg=self.colors['accent_success']
        ).pack(pady=(12, 8))
        
        vol_frame = tk.Frame(vol_card, bg=self.colors['bg_card'])
        vol_frame.pack(fill=tk.X, padx=20, pady=(0, 12))
        
        self.volume_var = tk.IntVar(value=70)
        volume_scale = tk.Scale(
            vol_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.volume_var,
            command=self.change_volume,
            bg=self.colors['bg_card'],
            fg=self.colors['text_primary'],
            troughcolor=self.colors['bg_dark'],
            activebackground=self.colors['accent_success'],
            highlightthickness=0,
            bd=0,
            showvalue=False,
            sliderrelief=tk.FLAT
        )
        volume_scale.pack(fill=tk.X, pady=(0, 8))
        
        self.label_vol = tk.Label(
            vol_frame,
            text="70%",
            bg=self.colors['bg_dark'],
            fg=self.colors['accent_success'],
            font=("Arial", 16, "bold"),
            padx=10,
            pady=5
        )
        self.label_vol.pack()
        
        # === COLONNE DROITE - PLAYLIST ===
        
        playlist_header = tk.Frame(right_frame, bg=self.colors['bg_card'])
        playlist_header.pack(fill=tk.X, pady=12, padx=12)
        
        tk.Label(
            playlist_header,
            text="📋 PLAYLIST",
            font=("Arial", 13, "bold"),
            bg=self.colors['bg_card'],
            fg=self.colors['accent_secondary']
        ).pack()
        
        self.label_playlist_count = tk.Label(
            playlist_header,
            text="0 pistes",
            font=("Arial", 8),
            bg=self.colors['bg_card'],
            fg=self.colors['text_secondary']
        )
        self.label_playlist_count.pack(pady=(3, 0))
        
        playlist_container = tk.Frame(right_frame, bg=self.colors['bg_card'])
        playlist_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
        
        scrollbar = tk.Scrollbar(playlist_container, bg=self.colors['bg_card'])
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.playlist_listbox = tk.Listbox(
            playlist_container,
            font=("Arial", 9),
            bg=self.colors['bg_dark'],
            fg=self.colors['text_primary'],
            selectbackground=self.colors['accent_primary'],
            selectforeground='white',
            yscrollcommand=scrollbar.set,
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0
        )
        self.playlist_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.playlist_listbox.yview)
        
        self.playlist_listbox.bind("<Double-Button-1>", self.load_from_playlist)
        
        playlist_btns = tk.Frame(right_frame, bg=self.colors['bg_card'])
        playlist_btns.pack(pady=12, padx=12, fill=tk.X)
        
        btn_clear = tk.Button(
            playlist_btns,
            text="✕ Vider",
            command=self.clear_playlist,
            font=("Arial", 9, "bold"),
            bg=self.colors['accent_danger'],
            fg='white',
            cursor="hand2",
            relief=tk.FLAT,
            padx=12,
            pady=6
        )
        btn_clear.pack(side=tk.LEFT, expand=True, padx=(0, 4))
        self.add_hover_effect(btn_clear, self.colors['accent_danger'], '#ee3644')
        
        btn_refresh = tk.Button(
            playlist_btns,
            text="↻ Actualiser",
            command=self.update_playlist_display,
            font=("Arial", 9, "bold"),
            bg=self.colors['bg_hover'],
            fg=self.colors['text_primary'],
            cursor="hand2",
            relief=tk.FLAT,
            padx=12,
            pady=6
        )
        btn_refresh.pack(side=tk.RIGHT, expand=True, padx=(4, 0))
        self.add_hover_effect(btn_refresh, self.colors['bg_hover'], self.colors['bg_card'])
    
    def add_hover_effect(self, widget, color_normal, color_hover):
        """Ajoute un effet de survol aux boutons"""
        widget.bind("<Enter>", lambda e: widget.config(bg=color_hover))
        widget.bind("<Leave>", lambda e: widget.config(bg=color_normal))
    
    def animate_equalizer(self):
        """Animation de l'égaliseur visuel"""
        if self.player.is_playing():
            for i in range(len(self.eq_target_heights)):
                if i < 8:
                    self.eq_target_heights[i] = random.randint(35, 80)
                elif i < 16:
                    self.eq_target_heights[i] = random.randint(25, 70)
                else:
                    self.eq_target_heights[i] = random.randint(15, 60)
        else:
            for i in range(len(self.eq_target_heights)):
                self.eq_target_heights[i] = max(0, self.eq_target_heights[i] - 5)
        
        for i in range(len(self.eq_heights)):
            diff = self.eq_target_heights[i] - self.eq_heights[i]
            self.eq_heights[i] += diff * 0.3
            
            height = int(self.eq_heights[i])
            if height > 60:
                color = self.colors['accent_danger']
            elif height > 40:
                color = self.colors['accent_secondary']
            elif height > 25:
                color = self.colors['accent_primary']
            else:
                color = self.colors['accent_success']
            
            bar = self.eq_bars[i]
            x1, _, x2, _ = self.eq_canvas.coords(bar)
            self.eq_canvas.coords(bar, x1, 80 - height, x2, 80)
            self.eq_canvas.itemconfig(bar, fill=color, outline=color)
        
        self.root.after(50, self.animate_equalizer)
    
    def load_files(self):
        """Charge les fichiers audio dans la playlist"""
        files = filedialog.askopenfilenames(
            title="Sélectionner des fichiers audio",
            filetypes=[
                ("Audio", "*.mp3 *.wav *.ogg *.flac *.m4a *.aac"),
                ("Tous", "*.*")
            ]
        )
        
        if files:
            self.playlist = list(files)
            self.current_index = 0
            self.moved_count = 0
            self.update_stats()
            self.update_playlist_display()
            
            if self.playlist:
                self.load_track(0)
                messagebox.showinfo("✅", f"{len(self.playlist)} fichiers chargés !")
    
    def update_playlist_display(self):
        """Met à jour l'affichage de la playlist"""
        self.playlist_listbox.delete(0, tk.END)
        for i, file in enumerate(self.playlist):
            filename = os.path.basename(file)
            prefix = "▶ " if i == self.current_index else "   "
            self.playlist_listbox.insert(tk.END, f"{prefix}{i+1}. {filename}")
            
            if i == self.current_index:
                self.playlist_listbox.itemconfig(i, bg=self.colors['accent_primary'], fg='white')
        
        count = len(self.playlist)
        self.label_playlist_count.config(text=f"{count} piste{'s' if count > 1 else ''}")
    
    def load_from_playlist(self, event):
        """Charge une piste depuis la playlist en double-cliquant"""
        selection = self.playlist_listbox.curselection()
        if selection:
            self.load_track(selection[0])
            if self.is_playing:
                self.player.play()
    
    def clear_playlist(self):
        """Vide la playlist"""
        if messagebox.askyesno("Confirmation", "Vider la playlist ?"):
            self.playlist = []
            self.current_index = 0
            self.update_playlist_display()
            self.label_track.config(text="Playlist vidée")
            self.label_pos.config(text="0 / 0")
            self.player.stop()
            self.is_playing = False
            self.btn_play.config(text="▶")
    
    def select_folder(self):
        """Sélectionne le dossier de destination pour les fichiers supprimés"""
        folder = filedialog.askdirectory()
        if folder:
            self.entry_folder.delete(0, tk.END)
            self.entry_folder.insert(0, folder)
            self.delete_folder = folder
    
    def load_track(self, index):
        """Charge une piste audio"""
        if 0 <= index < len(self.playlist):
            self.current_index = index
            path = self.playlist[index]
            
            try:
                media = self.instance.media_new(path)
                self.player.set_media(media)
                
                current_rate = self.tempo_var.get()
                self.player.set_rate(current_rate)
                
                name = os.path.basename(path)
                self.label_track.config(text=name)
                self.label_pos.config(text=f"Piste {index + 1} / {len(self.playlist)}")
                
                self.update_playlist_display()
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de charger:\n{e}")
    
    def toggle_play(self):
        """Lecture/Pause"""
        if not self.playlist:
            messagebox.showwarning("⚠️", "Chargez des fichiers d'abord !")
            return
        
        if self.is_playing:
            self.player.pause()
            self.is_playing = False
            self.btn_play.config(text="▶")
        else:
            self.player.play()
            self.is_playing = True
            self.btn_play.config(text="⏸⏸")
    
    def previous_track(self):
        """Piste précédente"""
        if not self.playlist:
            return
        if self.current_index > 0:
            self.load_track(self.current_index - 1)
            if self.is_playing:
                self.player.play()
        else:
            self.player.stop()
            self.player.play()
    
    def next_track(self):
        """Piste suivante"""
        if not self.playlist:
            return
        if self.current_index < len(self.playlist) - 1:
            self.load_track(self.current_index + 1)
            if self.is_playing:
                self.player.play()
        else:
            self.player.stop()
            self.is_playing = False
            self.btn_play.config(text="▶")
            messagebox.showinfo("✅", f"Playlist terminée!\n{self.moved_count} fichiers déplacés.")
    
    def delete_and_next(self):
        """Déplace le fichier actuel et passe au suivant"""
        if not self.playlist:
            return
        
        current_file = self.playlist[self.current_index]
        folder = self.entry_folder.get().strip()
        
        if not folder:
            messagebox.showerror("❌", "Spécifiez un dossier !")
            return
        
        try:
            os.makedirs(folder, exist_ok=True)
        except Exception as e:
            messagebox.showerror("❌", f"Erreur:\n{e}")
            return
        
        self.player.stop()
        self.is_playing = False
        self.btn_play.config(text="▶")
        time.sleep(0.3)
        
        try:
            filename = os.path.basename(current_file)
            dest = os.path.join(folder, filename)
            
            if os.path.exists(dest):
                base, ext = os.path.splitext(filename)
                i = 1
                while os.path.exists(dest):
                    dest = os.path.join(folder, f"{base}_{i}{ext}")
                    i += 1
            
            shutil.move(current_file, dest)
            self.moved_count += 1
            self.update_stats()
            
            self.playlist.pop(self.current_index)
            
            if self.current_index < len(self.playlist):
                self.load_track(self.current_index)
                self.player.play()
                self.is_playing = True
                self.btn_play.config(text="⏸⏸")
            else:
                if self.playlist:
                    self.current_index = len(self.playlist) - 1
                    self.load_track(self.current_index)
                else:
                    self.label_track.config(text="✅ Tous traités !")
                    self.label_pos.config(text="0 / 0")
                    self.update_playlist_display()
                    messagebox.showinfo("✅", f"Terminé!\n{self.moved_count} fichiers déplacés.")
        except Exception as e:
            messagebox.showerror("❌", f"Erreur:\n{e}")
    
    def change_tempo(self, val):
        """Modifie le tempo de lecture"""
        rate = float(val)
        self.player.set_rate(rate)
        percentage = int(rate * 100)
        self.label_tempo.config(text=f"{percentage}%")
    
    def set_tempo_preset(self, value):
        """Définit un tempo prédéfini"""
        self.tempo_var.set(value)
        self.player.set_rate(value)
        percentage = int(value * 100)
        self.label_tempo.config(text=f"{percentage}%")
    
    def seek_click(self, event):
        """Navigation dans la piste par clic"""
        if not self.is_playing and not self.player.is_playing():
            return
        
        width = self.progress_canvas.winfo_width()
        percent = max(0, min(1, event.x / width))
        duration = self.player.get_length()
        if duration > 0:
            new_pos = int(duration * percent)
            self.player.set_time(new_pos)
    
    def change_volume(self, val):
        """Modifie le volume"""
        vol = int(val)
        self.player.audio_set_volume(vol)
        self.label_vol.config(text=f"{vol}%")
    
    def update_stats(self):
        """Met à jour les statistiques"""
        self.label_stats.config(text=f"✓ Fichiers déplacés: {self.moved_count}")
    
    def update_timer(self):
        """Met à jour le timer et la barre de progression"""
        if self.player.is_playing():
            current_time = self.player.get_time()
            duration = self.player.get_length()
            
            if duration > 0 and current_time >= 0:
                curr_min = current_time // 60000
                curr_sec = (current_time % 60000) // 1000
                dur_min = duration // 60000
                dur_sec = (duration % 60000) // 1000
                
                self.label_time.config(text=f"{curr_min}:{curr_sec:02d} / {dur_min}:{dur_sec:02d}")
                
                width = self.progress_canvas.winfo_width()
                progress_width = (current_time / duration) * width
                self.progress_canvas.coords(self.progress_bar, 0, 0, progress_width, 6)
                
                if current_time >= duration - 500:
                    self.next_track()
        
        self.root.after(100, self.update_timer)

if __name__ == "__main__":
    root = tk.Tk()
    app = TrackSwipe(root)
    root.mainloop()

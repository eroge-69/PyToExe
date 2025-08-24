#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MKV Converter con Audio Italiano - Versione Desktop
Converte file MKV in MP4 selezionando automaticamente la traccia audio italiana
"""

import os
import subprocess
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import configparser
from pathlib import Path
import sys

__version__ = "1.0.0"
__author__ = "MKV Converter"


class MKVConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"MKV Converter v{__version__} - Audio Italiano")
        self.root.geometry("750x550")
        self.root.minsize(600, 400)

        # Icona della finestra (se disponibile)
        try:
            # Se hai un file .ico, puoi usarlo qui
            # self.root.iconbitmap("icon.ico")
            pass
        except:
            pass

        # File di configurazione
        if getattr(sys, 'frozen', False):
            # Se è un .exe compilato
            config_dir = Path.home()
        else:
            # Se è eseguito da sorgente
            config_dir = Path.cwd()

        self.config_file = config_dir / ".mkv_converter_config.ini"
        self.config = configparser.ConfigParser()

        # Variabili
        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.is_converting = False
        self.conversion_thread = None
        self.stop_requested = False

        # Carica configurazione
        self.load_config()

        # Crea interfaccia
        self.create_widgets()
        self.check_ffmpeg()

        # Gestione chiusura
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def check_ffmpeg(self):
        """Controlla se FFmpeg è disponibile"""
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            subprocess.run(["ffprobe", "-version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            messagebox.showwarning(
                "FFmpeg Non Trovato",
                "FFmpeg non è installato o non è nel PATH.\n\n"
                "Per utilizzare questo programma, scarica FFmpeg da:\n"
                "https://ffmpeg.org/download.html\n\n"
                "Il programma continuerà ma la conversione non funzionerà."
            )

    def create_widgets(self):
        """Crea l'interfaccia utente"""
        # Stile
        style = ttk.Style()

        # Frame principale con padding
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configurazione griglia responsiva
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Header con titolo
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))

        title_label = ttk.Label(header_frame, text="🎬 MKV Converter", font=('Arial', 16, 'bold'))
        title_label.pack(side=tk.LEFT)

        version_label = ttk.Label(header_frame, text=f"v{__version__}", font=('Arial', 9))
        version_label.pack(side=tk.RIGHT)

        # Sezione cartella input
        input_labelframe = ttk.LabelFrame(main_frame, text="📁 Cartella MKV di origine", padding="10")
        input_labelframe.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        input_labelframe.columnconfigure(0, weight=1)

        self.input_entry = ttk.Entry(input_labelframe, textvariable=self.input_folder, font=('Arial', 9))
        self.input_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))

        ttk.Button(input_labelframe, text="Sfoglia", command=self.select_input_folder).grid(row=0, column=1)

        # Sezione cartella output
        output_labelframe = ttk.LabelFrame(main_frame, text="💾 Cartella di destinazione", padding="10")
        output_labelframe.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        output_labelframe.columnconfigure(0, weight=1)

        self.output_entry = ttk.Entry(output_labelframe, textvariable=self.output_folder, font=('Arial', 9))
        self.output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))

        ttk.Button(output_labelframe, text="Sfoglia", command=self.select_output_folder).grid(row=0, column=1)

        # Frame controlli conversione
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=3, column=0, columnspan=3, pady=(0, 15))

        self.convert_button = ttk.Button(
            control_frame,
            text="🚀 Inizia Conversione",
            command=self.start_conversion,
            style="Accent.TButton"
        )
        self.convert_button.pack(side=tk.LEFT, padx=(0, 10))

        self.stop_button = ttk.Button(
            control_frame,
            text="⏹️ Ferma",
            command=self.stop_conversion,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT)

        # Sezione progresso
        progress_labelframe = ttk.LabelFrame(main_frame, text="📊 Progresso", padding="10")
        progress_labelframe.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        progress_labelframe.columnconfigure(0, weight=1)

        self.progress = ttk.Progressbar(progress_labelframe, mode='determinate', length=400)
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        self.progress_label = ttk.Label(progress_labelframe, text="Pronto", font=('Arial', 9))
        self.progress_label.grid(row=1, column=0, sticky=tk.W)

        # Sezione log
        log_labelframe = ttk.LabelFrame(main_frame, text="📋 Log attività", padding="10")
        log_labelframe.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_labelframe.columnconfigure(0, weight=1)
        log_labelframe.rowconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)

        # Text widget con scrollbar
        log_container = ttk.Frame(log_labelframe)
        log_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_container.columnconfigure(0, weight=1)
        log_container.rowconfigure(0, weight=1)

        self.log_text = tk.Text(
            log_container,
            height=8,
            wrap=tk.WORD,
            font=('Consolas', 9),
            bg='#f8f9fa',
            fg='#333'
        )

        log_scrollbar = ttk.Scrollbar(log_container, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.config(yscrollcommand=log_scrollbar.set)

        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Footer con info
        footer_frame = ttk.Frame(main_frame)
        footer_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))

        ttk.Label(
            footer_frame,
            text="💡 Seleziona automaticamente la traccia audio italiana • Richiede FFmpeg installato",
            font=('Arial', 8),
            foreground='#666'
        ).pack()

        # Messaggio iniziale
        self.log_message("🎬 MKV Converter pronto!")
        self.log_message("📋 Seleziona le cartelle e inizia la conversione")
        if self.input_folder.get():
            self.log_message(f"📁 Cartella input: {self.input_folder.get()}")
        if self.output_folder.get():
            self.log_message(f"💾 Cartella output: {self.output_folder.get()}")

    def load_config(self):
        """Carica configurazione salvata"""
        try:
            if self.config_file.exists():
                self.config.read(self.config_file)
                if 'Paths' in self.config:
                    self.input_folder.set(self.config.get('Paths', 'input_folder', fallback=''))
                    self.output_folder.set(self.config.get('Paths', 'output_folder', fallback=''))
        except Exception:
            pass

    def save_config(self):
        """Salva configurazione corrente"""
        try:
            if 'Paths' not in self.config:
                self.config.add_section('Paths')

            self.config.set('Paths', 'input_folder', self.input_folder.get())
            self.config.set('Paths', 'output_folder', self.output_folder.get())

            with open(self.config_file, 'w') as f:
                self.config.write(f)
        except Exception:
            pass

    def select_input_folder(self):
        """Seleziona cartella input"""
        initial_dir = self.input_folder.get() or str(Path.home())
        folder = filedialog.askdirectory(
            title="Seleziona cartella con file MKV",
            initialdir=initial_dir
        )
        if folder:
            self.input_folder.set(folder)
            self.log_message(f"📁 Selezionata cartella input: {folder}")

    def select_output_folder(self):
        """Seleziona cartella output"""
        initial_dir = self.output_folder.get() or str(Path.home())
        folder = filedialog.askdirectory(
            title="Seleziona cartella di destinazione",
            initialdir=initial_dir
        )
        if folder:
            self.output_folder.set(folder)
            self.log_message(f"💾 Selezionata cartella output: {folder}")

    def log_message(self, message):
        """Aggiunge messaggio al log"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def update_progress(self, current, total, filename=""):
        """Aggiorna barra di progresso"""
        if total > 0:
            percentage = (current / total) * 100
            self.progress['value'] = percentage

            if filename:
                self.progress_label.config(text=f"{current}/{total} - {percentage:.1f}% - {filename}")
            else:
                self.progress_label.config(text=f"{current}/{total} file - {percentage:.1f}%")
        else:
            self.progress['value'] = 0
            self.progress_label.config(text="Pronto")

        self.root.update_idletasks()

    def get_audio_streams_info(self, input_path):
        """Analizza tracce audio del file"""
        probe_command = [
            "ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", input_path
        ]
        try:
            result = subprocess.run(probe_command, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)

            audio_streams = []
            audio_index = 0
            for stream in data['streams']:
                if stream['codec_type'] == 'audio':
                    language = stream.get('tags', {}).get('language', 'und')
                    title = stream.get('tags', {}).get('title', '')
                    audio_streams.append({
                        'audio_index': audio_index,
                        'language': language,
                        'title': title
                    })
                    audio_index += 1

            return audio_streams
        except Exception as e:
            self.log_message(f"⚠️  Errore analisi audio: {e}")
            return []

    def find_italian_audio_stream(self, audio_streams):
        """Trova traccia audio italiana"""
        # Prima priorità: lingua italiana
        for stream in audio_streams:
            if stream['language'].lower() in ['it', 'ita', 'italian']:
                return stream['audio_index']

        # Seconda priorità: titolo che contiene "italian" o "ita"
        for stream in audio_streams:
            title = stream['title'].lower()
            if 'italian' in title or 'ita' in title:
                return stream['audio_index']

        # Default: prima traccia
        return 0

    def convert_files(self):
        """Processo conversione (thread separato)"""
        try:
            input_dir = self.input_folder.get()
            output_dir = self.output_folder.get()

            # Validazione
            if not input_dir or not output_dir:
                messagebox.showerror("Errore", "Seleziona entrambe le cartelle")
                return

            if not os.path.exists(input_dir):
                messagebox.showerror("Errore", "Cartella input non esistente")
                return

            # Crea cartelle output
            subtitles_folder = os.path.join(output_dir, "sottotitoli")
            os.makedirs(output_dir, exist_ok=True)
            os.makedirs(subtitles_folder, exist_ok=True)

            # Trova file MKV
            mkv_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".mkv")]
            total_files = len(mkv_files)

            if total_files == 0:
                self.log_message("❌ Nessun file MKV trovato")
                messagebox.showinfo("Info", "Nessun file MKV trovato nella cartella selezionata")
                return

            self.log_message(f"🎬 Trovati {total_files} file MKV da convertire")
            self.log_message("━" * 50)

            successful_conversions = 0

            for i, filename in enumerate(mkv_files):
                if self.stop_requested:
                    self.log_message("⏹️  Conversione fermata dall'utente")
                    break

                current_file = i + 1
                self.log_message(f"\n📁 [{current_file}/{total_files}] {filename}")
                self.update_progress(i, total_files, filename)

                input_path = os.path.join(input_dir, filename)
                output_filename = os.path.splitext(filename)[0] + ".mp4"
                output_path = os.path.join(output_dir, output_filename)

                # Skip se file output già esistente
                if os.path.exists(output_path):
                    self.log_message(f"⚠️  File già esistente, salto: {output_filename}")
                    continue

                try:
                    # Analizza audio
                    audio_streams = self.get_audio_streams_info(input_path)
                    italian_stream_index = self.find_italian_audio_stream(audio_streams)

                    if audio_streams:
                        self.log_message(f"🎵 Tracce audio trovate: {len(audio_streams)}")
                        for stream in audio_streams:
                            lang_info = f"{stream['language']}"
                            if stream['title']:
                                lang_info += f" ({stream['title']})"
                            marker = "👈 SELEZIONATA" if stream['audio_index'] == italian_stream_index else ""
                            self.log_message(f"   • Stream {stream['audio_index']}: {lang_info} {marker}")

                    # Estrai sottotitoli
                    subtitles_path = os.path.join(subtitles_folder, os.path.splitext(filename)[0] + ".vtt")
                    extract_subtitles_command = [
                        "ffmpeg", "-y", "-v", "quiet", "-i", input_path,
                        "-map", "0:s:0", "-c:s", "webvtt", subtitles_path
                    ]

                    subprocess.run(extract_subtitles_command, check=False)

                    # Converti video
                    command = [
                        "ffmpeg", "-y", "-v", "quiet", "-stats", "-i", input_path,
                        "-map", "0:v:0",
                        "-map", f"0:a:{italian_stream_index}",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                        output_path
                    ]

                    self.log_message("🔄 Conversione in corso...")
                    result = subprocess.run(command, check=True)

                    # Verifica file creato
                    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                        file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
                        self.log_message(f"✅ Convertito con successo! ({file_size:.1f} MB)")
                        successful_conversions += 1
                    else:
                        self.log_message("❌ Errore: file di output non creato")

                except subprocess.CalledProcessError as e:
                    self.log_message(f"❌ Errore FFmpeg: {e}")
                except Exception as e:
                    self.log_message(f"❌ Errore imprevisto: {e}")

            # Riepilogo finale
            if not self.stop_requested:
                self.update_progress(total_files, total_files)
                self.log_message("\n" + "=" * 50)
                self.log_message(f"🎉 COMPLETATO!")
                self.log_message(f"✅ File convertiti con successo: {successful_conversions}/{total_files}")

                if successful_conversions > 0:
                    messagebox.showinfo("Completato!",
                                        f"Conversione completata!\n\n✅ {successful_conversions} file convertiti con successo")
                else:
                    messagebox.showwarning("Attenzione", "Nessun file è stato convertito con successo")

        except Exception as e:
            self.log_message(f"\n❌ ERRORE GENERALE: {e}")
            messagebox.showerror("Errore", f"Errore durante la conversione:\n{e}")

        finally:
            self.is_converting = False
            self.stop_requested = False
            self.convert_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            if not self.stop_requested:
                self.update_progress(0, 0)

    def start_conversion(self):
        """Avvia conversione"""
        if not self.input_folder.get().strip():
            messagebox.showerror("Errore", "Seleziona la cartella con i file MKV")
            return

        if not self.output_folder.get().strip():
            messagebox.showerror("Errore", "Seleziona la cartella di destinazione")
            return

        # Conferma se cartelle uguali
        if os.path.normpath(self.input_folder.get()) == os.path.normpath(self.output_folder.get()):
            if not messagebox.askyesno("Conferma",
                                       "Le cartelle di input e output sono uguali.\n"
                                       "I file originali potrebbero essere sovrascritti.\n\n"
                                       "Vuoi continuare?"):
                return

        # Pulisci log
        self.log_text.delete(1.0, tk.END)

        # Avvia conversione
        self.is_converting = True
        self.stop_requested = False
        self.convert_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        self.conversion_thread = threading.Thread(target=self.convert_files)
        self.conversion_thread.daemon = True
        self.conversion_thread.start()

    def stop_conversion(self):
        """Ferma conversione"""
        if self.is_converting:
            self.stop_requested = True
            self.stop_button.config(state=tk.DISABLED)
            self.log_message("\n⏹️  Richiesta di stop inviata...")

    def on_closing(self):
        """Gestisce chiusura applicazione"""
        if self.is_converting:
            if messagebox.askyesno("Conferma Uscita",
                                   "Conversione in corso.\n\nVuoi davvero chiudere l'applicazione?"):
                self.stop_requested = True
                self.save_config()
                self.root.destroy()
        else:
            self.save_config()
            self.root.destroy()


def main():
    """Funzione principale"""
    try:
        root = tk.Tk()

        # Configura stile se disponibile
        try:
            root.tk.call('source', 'azure.tcl')
            root.tk.call('set_theme', 'light')
        except:
            pass

        app = MKVConverterGUI(root)
        root.mainloop()

    except Exception as e:
        messagebox.showerror("Errore Critico", f"Errore durante l'avvio:\n{e}")


if __name__ == "__main__":
    main()
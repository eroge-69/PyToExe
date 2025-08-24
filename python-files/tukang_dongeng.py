import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from gtts import gTTS
import pygame
import os
import threading
from datetime import datetime
import tempfile

class TextToSpeechApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Text to Speech Converter")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Inisialisasi pygame mixer
        pygame.mixer.init()
        
        self.setup_ui()
        self.current_audio_file = None
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Text to Speech Converter", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Text input label
        ttk.Label(main_frame, text="Masukkan Teks:", 
                 font=("Arial", 11)).grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        # Text area dengan scrollbar
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.text_area = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, 
                                                  width=60, height=10,
                                                  font=("Arial", 10))
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # Language selection
        ttk.Label(main_frame, text="Pilih Bahasa:", 
                 font=("Arial", 11)).grid(row=3, column=0, sticky=tk.W, pady=(10, 5))
        
        self.language_var = tk.StringVar(value="id")
        language_combo = ttk.Combobox(main_frame, textvariable=self.language_var,
                                     values=["id", "en", "es", "fr", "de", "ja"],
                                     state="readonly", width=10)
        language_combo.grid(row=3, column=0, sticky=tk.E, pady=(10, 5))
        
        # Language labels
        language_labels = ttk.Label(main_frame, text="id: Indonesia, en: English, es: Spanish, fr: French, de: German, ja: Japanese",
                                   font=("Arial", 8), foreground="gray")
        language_labels.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        # Convert button
        self.convert_btn = ttk.Button(button_frame, text="Convert to Speech", 
                                     command=self.convert_text)
        self.convert_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Play button
        self.play_btn = ttk.Button(button_frame, text="Play", 
                                  command=self.play_audio, state=tk.DISABLED)
        self.play_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Stop button
        self.stop_btn = ttk.Button(button_frame, text="Stop", 
                                  command=self.stop_audio, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear button
        self.clear_btn = ttk.Button(button_frame, text="Clear", 
                                   command=self.clear_text)
        self.clear_btn.pack(side=tk.LEFT)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Siap", foreground="green")
        self.status_label.grid(row=6, column=0, columnspan=2, pady=(10, 0))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
    def convert_text(self):
        text = self.text_area.get("1.0", tk.END).strip()
        
        if not text:
            messagebox.showwarning("Peringatan", "Silakan masukkan teks terlebih dahulu!")
            return
        
        # Disable button during conversion
        self.convert_btn.config(state=tk.DISABLED)
        self.play_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Mengonversi...", foreground="orange")
        self.progress.start()
        
        # Run conversion in separate thread
        thread = threading.Thread(target=self._convert_thread, args=(text,))
        thread.daemon = True
        thread.start()
        
    def _convert_thread(self, text):
        try:
            language = self.language_var.get()
            tts = gTTS(text=text, lang=language, slow=False)
            
            # Create temporary file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_file = os.path.join(tempfile.gettempdir(), f"tts_{timestamp}.mp3")
            
            tts.save(temp_file)
            self.current_audio_file = temp_file
            
            # Update UI in main thread
            self.root.after(0, self._conversion_complete)
            
        except Exception as e:
            self.root.after(0, self._conversion_error, str(e))
    
    def _conversion_complete(self):
        self.progress.stop()
        self.convert_btn.config(state=tk.NORMAL)
        self.play_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Konversi selesai! Klik Play untuk mendengarkan", 
                                foreground="green")
    
    def _conversion_error(self, error_msg):
        self.progress.stop()
        self.convert_btn.config(state=tk.NORMAL)
        self.status_label.config(text=f"Error: {error_msg}", foreground="red")
        messagebox.showerror("Error", f"Terjadi kesalahan: {error_msg}")
    
    def play_audio(self):
        if self.current_audio_file and os.path.exists(self.current_audio_file):
            try:
                pygame.mixer.music.load(self.current_audio_file)
                pygame.mixer.music.play()
                self.play_btn.config(state=tk.DISABLED)
                self.stop_btn.config(state=tk.NORMAL)
                self.status_label.config(text="Memutar audio...", foreground="blue")
                
                # Check when playback finishes
                self.root.after(100, self._check_playback)
                
            except Exception as e:
                messagebox.showerror("Error", f"Gagal memutar audio: {str(e)}")
    
    def _check_playback(self):
        if pygame.mixer.music.get_busy():
            self.root.after(100, self._check_playback)
        else:
            self.play_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.status_label.config(text="Pemutaran selesai", foreground="green")
    
    def stop_audio(self):
        pygame.mixer.music.stop()
        self.play_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Dihentikan", foreground="orange")
    
    def clear_text(self):
        self.text_area.delete("1.0", tk.END)
        self.status_label.config(text="Teks dibersihkan", foreground="green")
        
        # Stop any playing audio
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            self.play_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
    
    def cleanup(self):
        """Clean up temporary files"""
        if self.current_audio_file and os.path.exists(self.current_audio_file):
            try:
                os.remove(self.current_audio_file)
            except:
                pass

def main():
    root = tk.Tk()
    app = TextToSpeechApp(root)
    
    # Cleanup on exit
    def on_closing():
        app.cleanup()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import yt_dlp
import threading
import os
from pathlib import Path
import subprocess
import platform

class YouTubeDownloaderUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("YouTube Downloader")
        self.root.geometry("500x450")
        self.root.configure(bg='#0d1117')
        self.root.resizable(False, False)
        
        # Language settings
        self.current_language = 'en'
        self.languages = {
            'en': {
                'title': 'YouTube Downloader',
                'url_label': 'YouTube URL:',
                'url_placeholder': 'Paste YouTube URL here...',
                'format_label': 'Choose Format:',
                'output_label': 'Download to:',
                'browse_btn': 'Change',
                'download_btn': 'Download',
                'language_btn': 'EN',
                'mp3_btn': 'MP3 (Audio)',
                'mp4_btn': 'MP4 (Video)',
                'other_formats': 'Other formats...',
                'downloading': 'Downloading...',
                'download_complete': 'Download Complete!',
                'download_failed': 'Download Failed',
                'retrying': 'Retrying download...',
                'error': 'Error',
                'success': 'Success',
                'no_url': 'Please enter a YouTube URL',
                'getting_formats': 'Loading formats...',
                'formats_error': 'Error getting formats. Please check the URL.',
                'ok_btn': 'OK',
                'show_folder_btn': 'Show in Folder'
            },
            'ua': {
                'title': 'YouTube Завантажувач',
                'url_label': 'YouTube URL:',
                'url_placeholder': 'Вставте YouTube URL тут...',
                'format_label': 'Оберіть формат:',
                'output_label': 'Завантажити в:',
                'browse_btn': 'Змінити',
                'download_btn': 'Завантажити',
                'language_btn': 'UA',
                'mp3_btn': 'MP3 (Аудіо)',
                'mp4_btn': 'MP4 (Відео)',
                'other_formats': 'Інші формати...',
                'downloading': 'Завантаження...',
                'download_complete': 'Завантаження завершено!',
                'download_failed': 'Помилка завантаження',
                'retrying': 'Повторна спроба...',
                'error': 'Помилка',
                'success': 'Успіх',
                'no_url': 'Будь ласка, введіть YouTube URL',
                'getting_formats': 'Завантаження форматів...',
                'formats_error': 'Помилка отримання форматів. Перевірте URL.',
                'ok_btn': 'OK',
                'show_folder_btn': 'Показати в папці'
            }
        }
        
        # Default download folder
        self.download_folder = str(Path.home() / "Downloads")
        
        # Format selection
        self.selected_format = "mp4"  # Default to MP4
        self.available_formats = []
        self.other_formats_visible = False
        
        # Download path for completion dialog
        self.last_download_path = None
        
        self.setup_ui()
        
    def get_text(self, key):
        return self.languages[self.current_language][key]
        
    def setup_ui(self):
        # Main container
        main_frame = tk.Frame(self.root, bg='#0d1117')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Header with title and language toggle
        header_frame = tk.Frame(main_frame, bg='#0d1117')
        header_frame.pack(fill='x', pady=(0, 20))
        
        title_label = tk.Label(
            header_frame,
            text=self.get_text('title'),
            font=('Arial', 16, 'bold'),
            fg='#f0f6fc',
            bg='#0d1117'
        )
        title_label.pack(side='left')
        
        self.language_btn = tk.Button(
            header_frame,
            text=self.get_text('language_btn'),
            font=('Arial', 9),
            bg='#21262d',
            fg='#f0f6fc',
            relief='flat',
            padx=15,
            pady=5,
            command=self.toggle_language,
            cursor='hand2'
        )
        self.language_btn.pack(side='right')
        
        # URL input
        url_label = tk.Label(
            main_frame,
            text=self.get_text('url_label'),
            font=('Arial', 10),
            fg='#8b949e',
            bg='#0d1117'
        )
        url_label.pack(anchor='w', pady=(0, 5))
        
        self.url_entry = tk.Entry(
            main_frame,
            font=('Arial', 11),
            bg='#21262d',
            fg='#f0f6fc',
            relief='flat',
            bd=0,
            insertbackground='#f0f6fc'
        )
        self.url_entry.pack(fill='x', pady=(0, 20), ipady=8)
        self.url_entry.insert(0, self.get_text('url_placeholder'))
        self.url_entry.bind('<FocusIn>', self.on_url_focus_in)
        self.url_entry.bind('<FocusOut>', self.on_url_focus_out)
        self.url_entry.config(fg='#6e7681')
        
        # Format selection
        format_label = tk.Label(
            main_frame,
            text=self.get_text('format_label'),
            font=('Arial', 10),
            fg='#8b949e',
            bg='#0d1117'
        )
        format_label.pack(anchor='w', pady=(0, 10))
        
        # Format buttons frame
        format_frame = tk.Frame(main_frame, bg='#0d1117')
        format_frame.pack(fill='x', pady=(0, 10))
        
        # MP3 and MP4 buttons
        self.mp3_btn = tk.Button(
            format_frame,
            text=self.get_text('mp3_btn'),
            font=('Arial', 10, 'bold'),
            bg='#238636',
            fg='white',
            relief='flat',
            padx=20,
            pady=8,
            command=lambda: self.select_format('mp3'),
            cursor='hand2'
        )
        self.mp3_btn.pack(side='left', padx=(0, 10))
        
        self.mp4_btn = tk.Button(
            format_frame,
            text=self.get_text('mp4_btn'),
            font=('Arial', 10, 'bold'),
            bg='#1f6feb',
            fg='white',
            relief='flat',
            padx=20,
            pady=8,
            command=lambda: self.select_format('mp4'),
            cursor='hand2'
        )
        self.mp4_btn.pack(side='left', padx=(0, 10))
        
        # Other formats button
        self.other_btn = tk.Button(
            format_frame,
            text=self.get_text('other_formats'),
            font=('Arial', 9),
            bg='#21262d',
            fg='#8b949e',
            relief='flat',
            padx=15,
            pady=8,
            command=self.toggle_other_formats,
            cursor='hand2'
        )
        self.other_btn.pack(side='left')
        
        # Other formats dropdown (initially hidden)
        self.format_var = tk.StringVar()
        self.format_dropdown = ttk.Combobox(
            main_frame,
            textvariable=self.format_var,
            font=('Arial', 9),
            state='readonly',
            width=60
        )
        # Don't pack initially - will be shown when needed
        
        # Download location
        location_label = tk.Label(
            main_frame,
            text=self.get_text('output_label'),
            font=('Arial', 10),
            fg='#8b949e',
            bg='#0d1117'
        )
        location_label.pack(anchor='w', pady=(20, 5))
        
        location_frame = tk.Frame(main_frame, bg='#0d1117')
        location_frame.pack(fill='x', pady=(0, 20))
        
        self.folder_label = tk.Label(
            location_frame,
            text=self.download_folder,
            font=('Arial', 9),
            fg='#6e7681',
            bg='#21262d',
            relief='flat',
            anchor='w',
            padx=10,
            pady=6
        )
        self.folder_label.pack(side='left', fill='x', expand=True)
        
        browse_btn = tk.Button(
            location_frame,
            text=self.get_text('browse_btn'),
            font=('Arial', 9),
            bg='#21262d',
            fg='#f0f6fc',
            relief='flat',
            padx=15,
            pady=6,
            command=self.browse_folder,
            cursor='hand2'
        )
        browse_btn.pack(side='right', padx=(10, 0))
        
        # Progress
        self.progress_label = tk.Label(
            main_frame,
            text="",
            font=('Arial', 9),
            fg='#8b949e',
            bg='#0d1117'
        )
        self.progress_label.pack(pady=(0, 15))
        
        # Download button
        self.download_btn = tk.Button(
            main_frame,
            text=self.get_text('download_btn'),
            font=('Arial', 12, 'bold'),
            bg='#238636',
            fg='white',
            relief='flat',
            padx=40,
            pady=12,
            command=self.download_video,
            cursor='hand2'
        )
        self.download_btn.pack(pady=10)
        
        # Configure ttk style for dark theme
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TCombobox', 
                       fieldbackground='#21262d', 
                       background='#21262d', 
                       foreground='#f0f6fc',
                       borderwidth=0)
        
        # Set initial format selection
        self.update_format_buttons()
        
    def toggle_language(self):
        self.current_language = 'ua' if self.current_language == 'en' else 'en'
        self.update_ui_text()
        
    def update_ui_text(self):
        self.language_btn.config(text=self.get_text('language_btn'))
        self.mp3_btn.config(text=self.get_text('mp3_btn'))
        self.mp4_btn.config(text=self.get_text('mp4_btn'))
        self.other_btn.config(text=self.get_text('other_formats'))
        self.download_btn.config(text=self.get_text('download_btn'))
        
        # Update placeholder
        current_text = self.url_entry.get()
        if current_text in [self.languages['en']['url_placeholder'], self.languages['ua']['url_placeholder']]:
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, self.get_text('url_placeholder'))
            self.url_entry.config(fg='#6e7681')
            
    def select_format(self, format_type):
        self.selected_format = format_type
        self.update_format_buttons()
        # Hide other formats if visible
        if self.other_formats_visible:
            self.toggle_other_formats()
            
    def update_format_buttons(self):
        # Reset all buttons
        self.mp3_btn.config(bg='#21262d', fg='#8b949e')
        self.mp4_btn.config(bg='#21262d', fg='#8b949e')
        
        # Highlight selected
        if self.selected_format == 'mp3':
            self.mp3_btn.config(bg='#238636', fg='white')
        elif self.selected_format == 'mp4':
            self.mp4_btn.config(bg='#1f6feb', fg='white')
            
    def toggle_other_formats(self):
        if not self.other_formats_visible:
            # Load formats first
            self.load_other_formats()
        else:
            # Hide dropdown
            self.format_dropdown.pack_forget()
            self.other_formats_visible = False
            self.other_btn.config(text=self.get_text('other_formats'))
            
    def load_other_formats(self):
        url = self.url_entry.get()
        if not url or url == self.get_text('url_placeholder'):
            messagebox.showerror(self.get_text('error'), self.get_text('no_url'))
            return
            
        def fetch_formats():
            try:
                self.root.after(0, lambda: self.progress_label.config(text=self.get_text('getting_formats')))
                
                ydl_opts = {'quiet': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    formats = info.get('formats', [])
                    
                    format_list = []
                    for f in formats:
                        ext = f.get('ext', '')
                        quality = f.get('format_note', f.get('height', ''))
                        format_id = f.get('format_id', '')
                        
                        if ext and quality:
                            format_str = f"{ext.upper()} - {quality} ({format_id})"
                            format_list.append(format_str)
                    
                    self.available_formats = format_list
                    self.root.after(0, self.show_other_formats)
                    
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(
                    self.get_text('error'), 
                    self.get_text('formats_error')
                ))
            finally:
                self.root.after(0, lambda: self.progress_label.config(text=""))
                
        threading.Thread(target=fetch_formats, daemon=True).start()
        
    def show_other_formats(self):
        if self.available_formats:
            self.format_dropdown['values'] = self.available_formats
            self.format_dropdown.set(self.available_formats[0])
            self.format_dropdown.pack(fill='x', pady=(5, 0))
            self.other_formats_visible = True
            self.other_btn.config(text="Hide formats")
            self.selected_format = 'custom'
            self.update_format_buttons()
            
    def on_url_focus_in(self, event):
        if self.url_entry.get() == self.get_text('url_placeholder'):
            self.url_entry.delete(0, tk.END)
            self.url_entry.config(fg='#f0f6fc')
            
    def on_url_focus_out(self, event):
        if not self.url_entry.get():
            self.url_entry.insert(0, self.get_text('url_placeholder'))
            self.url_entry.config(fg='#6e7681')
            
    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.download_folder)
        if folder:
            self.download_folder = folder
            self.folder_label.config(text=folder)
            
    def download_video(self):
        url = self.url_entry.get()
        if not url or url == self.get_text('url_placeholder'):
            messagebox.showerror(self.get_text('error'), self.get_text('no_url'))
            return
            
        def download_with_retry(max_retries=2):
            for attempt in range(max_retries + 1):
                try:
                    if attempt > 0:
                        self.root.after(0, lambda: self.progress_label.config(
                            text=f"{self.get_text('retrying')} ({attempt}/{max_retries})"
                        ))
                    else:
                        self.root.after(0, lambda: self.progress_label.config(text=self.get_text('downloading')))
                    
                    self.root.after(0, lambda: self.download_btn.config(state='disabled'))
                    
                    # Determine format options
                    if self.selected_format == 'mp3':
                        ydl_opts = {
                            'format': 'bestaudio/best',
                            'outtmpl': os.path.join(self.download_folder, '%(title)s.%(ext)s'),
                            'postprocessors': [{
                                'key': 'FFmpegExtractAudio',
                                'preferredcodec': 'mp3',
                                'preferredquality': '192',
                            }],
                        }
                    elif self.selected_format == 'mp4':
                        ydl_opts = {
                            'format': 'best[ext=mp4]/best',
                            'outtmpl': os.path.join(self.download_folder, '%(title)s.%(ext)s'),
                        }
                    else:  # custom format
                        selected_format = self.format_var.get()
                        format_id = selected_format.split('(')[-1].split(')')[0]
                        ydl_opts = {
                            'format': format_id,
                            'outtmpl': os.path.join(self.download_folder, '%(title)s.%(ext)s'),
                        }
                    
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                        title = info.get('title', 'download')
                        ext = 'mp3' if self.selected_format == 'mp3' else info.get('ext', 'mp4')
                        
                        # Download
                        ydl.download([url])
                        
                        # Store path for completion dialog
                        self.last_download_path = os.path.join(self.download_folder, f"{title}.{ext}")
                        
                    # Success - show completion dialog
                    self.root.after(0, self.show_completion_dialog)
                    return
                    
                except Exception as e:
                    if attempt < max_retries:
                        continue  # Try again
                    else:
                        # Final failure
                        self.root.after(0, lambda: messagebox.showerror(
                            self.get_text('error'), 
                            f"{self.get_text('download_failed')}: {str(e)}"
                        ))
                        return
                finally:
                    if attempt == max_retries:  # Last attempt
                        self.root.after(0, lambda: self.download_btn.config(state='normal'))
                        self.root.after(0, lambda: self.progress_label.config(text=""))
                
        threading.Thread(target=download_with_retry, daemon=True).start()
        
    def show_completion_dialog(self):
        # Create custom dialog
        dialog = tk.Toplevel(self.root)
        dialog.title(self.get_text('success'))
        dialog.geometry("300x120")
        dialog.configure(bg='#0d1117')
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 100,
            self.root.winfo_rooty() + 100
        ))
        
        # Success message
        message_label = tk.Label(
            dialog,
            text=self.get_text('download_complete'),
            font=('Arial', 11),
            fg='#f0f6fc',
            bg='#0d1117'
        )
        message_label.pack(pady=20)
        
        # Buttons frame
        btn_frame = tk.Frame(dialog, bg='#0d1117')
        btn_frame.pack(pady=10)
        
        # OK button
        ok_btn = tk.Button(
            btn_frame,
            text=self.get_text('ok_btn'),
            font=('Arial', 10),
            bg='#21262d',
            fg='#f0f6fc',
            relief='flat',
            padx=20,
            pady=8,
            command=dialog.destroy,
            cursor='hand2'
        )
        ok_btn.pack(side='left', padx=(0, 10))
        
        # Show in folder button
        folder_btn = tk.Button(
            btn_frame,
            text=self.get_text('show_folder_btn'),
            font=('Arial', 10),
            bg='#238636',
            fg='white',
            relief='flat',
            padx=20,
            pady=8,
            command=lambda: self.show_in_folder(dialog),
            cursor='hand2'
        )
        folder_btn.pack(side='left')
        
    def show_in_folder(self, dialog):
        try:
            if platform.system() == "Windows":
                os.startfile(self.download_folder)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", self.download_folder])
            else:  # Linux
                subprocess.run(["xdg-open", self.download_folder])
        except Exception as e:
            print(f"Could not open folder: {e}")
        
        dialog.destroy()
        
    def run(self):
        self.root.mainloop()

# Create and run the application$ pip install auto-py-to-exe
if __name__ == "__main__":
    app = YouTubeDownloaderUI()
    app.run()
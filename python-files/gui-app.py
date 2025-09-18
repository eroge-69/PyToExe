import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import threading
import time
import os
import re
import shutil
import json
import sys
import requests
from datetime import datetime
import queue
import webbrowser
from PIL import Image, ImageTk, ImageDraw, ImageFilter
import io
import glob

# Constant downloads directory
DOWNLOADS_DIR = "downloads"

# Try to import mutagen for MP3 metadata handling
try:
    from mutagen.mp3 import MP3
    from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False

class ModernButton(tk.Frame):
    """Custom modern button with hover effects"""
    def __init__(self, parent, text="", command=None, bg="#3B82F6", fg="white", width=200, height=40):
        # Determine a safe background for ttk/tk parents
        def _safe_parent_bg(widget):
            try:
                return widget.cget('background')
            except Exception:
                try:
                    return widget.cget('bg')
                except Exception:
                    try:
                        return widget.winfo_toplevel().cget('bg')
                    except Exception:
                        return "#1F2937"

        super().__init__(parent, bg=_safe_parent_bg(parent))
        
        self.command = command
        self.default_bg = bg
        self.hover_bg = self._adjust_color(bg, 20)
        self.active_bg = self._adjust_color(bg, -20)
        
        self.canvas = tk.Canvas(self, width=width, height=height, highlightthickness=0)
        self.canvas.pack()
        
        self.rect = self.canvas.create_rectangle(
            2, 2, width-2, height-2, 
            fill=bg, outline="", width=0
        )
        
        self.text = self.canvas.create_text(
            width//2, height//2, 
            text=text, fill=fg, 
            font=("Segoe UI", 11, "bold")
        )
        
        self.canvas.bind("<Enter>", self._on_enter)
        self.canvas.bind("<Leave>", self._on_leave)
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        
    def _adjust_color(self, hex_color, brightness):
        """Adjust color brightness"""
        rgb = tuple(int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        rgb = tuple(max(0, min(255, c + brightness)) for c in rgb)
        return '#{:02x}{:02x}{:02x}'.format(*rgb)
    
    def _on_enter(self, e):
        self.canvas.itemconfig(self.rect, fill=self.hover_bg)
        
    def _on_leave(self, e):
        self.canvas.itemconfig(self.rect, fill=self.default_bg)
        
    def _on_click(self, e):
        self.canvas.itemconfig(self.rect, fill=self.active_bg)
        
    def _on_release(self, e):
        self.canvas.itemconfig(self.rect, fill=self.hover_bg)
        if self.command:
            self.command()
            
    def set_state(self, state):
        if state == 'disabled':
            self.canvas.itemconfig(self.rect, fill="#9CA3AF")
            self.canvas.unbind("<Enter>")
            self.canvas.unbind("<Leave>")
            self.canvas.unbind("<Button-1>")
            self.canvas.unbind("<ButtonRelease-1>")
        else:
            self.canvas.itemconfig(self.rect, fill=self.default_bg)
            self.canvas.bind("<Enter>", self._on_enter)
            self.canvas.bind("<Leave>", self._on_leave)
            self.canvas.bind("<Button-1>", self._on_click)
            self.canvas.bind("<ButtonRelease-1>", self._on_release)

class AnimatedProgressBar(tk.Canvas):
    """Custom animated progress bar"""
    def __init__(self, parent, width=400, height=6):
        super().__init__(parent, width=width, height=height, highlightthickness=0, bg="#1F2937")
        
        self.width = width
        self.height = height
        
        # Background
        self.create_rectangle(0, 0, width, height, fill="#374151", outline="")
        
        # Progress bar
        self.progress = self.create_rectangle(0, 0, 0, height, fill="#3B82F6", outline="")
        self.glow = self.create_rectangle(0, 0, 0, height, fill="#60A5FA", outline="")
        
        self.value = 0
        self.target_value = 0
        self.animating = False
        
    def set_value(self, value):
        """Set progress value (0-100)"""
        self.target_value = max(0, min(100, value))
        if not self.animating:
            self.animate()
            
    def animate(self):
        """Smooth animation"""
        if abs(self.value - self.target_value) > 0.5:
            self.animating = True
            diff = self.target_value - self.value
            self.value += diff * 0.1
            
            progress_width = (self.value / 100) * self.width
            self.coords(self.progress, 0, 0, progress_width, self.height)
            self.coords(self.glow, max(0, progress_width-20), 0, progress_width, self.height)
            
            self.after(10, self.animate)
        else:
            self.animating = False
            self.value = self.target_value

class YouTubeDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Playlist Downloader Pro")
        self.root.geometry("900x700")
        self.root.configure(bg="#1F2937")
        
        # Set window icon (if available)
        try:
            self.root.iconbitmap(default='icon.ico')
        except:
            pass
        
        # Variables
        self.playlist_url = tk.StringVar()
        self.output_dir = tk.StringVar(value="downloads")
        self.quality = tk.StringVar(value="320k")
        self.download_queue = queue.Queue()
        self.is_downloading = False
        self.total_videos = 0
        self.current_video = 0
        self.videos_info = []
        
        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.configure_styles()
        self.create_widgets()
        self.center_window()
        
        # Resolve external tool paths once
        self.yt_dlp_path = self._resolve_tool_path("yt-dlp")
        self.ffmpeg_path = self._resolve_tool_path("ffmpeg")

    def _resource_base_dir(self):
        """Return base directory for bundled resources (supports PyInstaller one-file)."""
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            return sys._MEIPASS
        return os.path.dirname(os.path.abspath(__file__))

    def _resolve_tool_path(self, tool_name):
        """Find bundled tool (yt-dlp.exe/ffmpeg.exe) or fallback to PATH."""
        base = self._resource_base_dir()
        # Check current dir
        candidates = [
            os.path.join(base, f"{tool_name}.exe"),
            os.path.join(base, tool_name),
        ]
        for c in candidates:
            if os.path.exists(c):
                return c
        # Fallback to PATH
        return shutil.which(tool_name)
        
    def configure_styles(self):
        """Configure custom styles"""
        # Dark theme colors
        bg_color = "#1F2937"
        fg_color = "#F9FAFB"
        select_bg = "#3B82F6"
        
        self.style.configure("Dark.TFrame", background=bg_color)
        self.style.configure("Dark.TLabel", background=bg_color, foreground=fg_color)
        self.style.configure("Title.TLabel", background=bg_color, foreground=fg_color, 
                           font=("Segoe UI", 24, "bold"))
        self.style.configure("Subtitle.TLabel", background=bg_color, foreground="#9CA3AF",
                           font=("Segoe UI", 10))
        self.style.configure("Heading.TLabel", background=bg_color, foreground=fg_color,
                           font=("Segoe UI", 12, "bold"))
        
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, style="Dark.TFrame", padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with gradient effect
        self.create_header(main_frame)
        
        # Input section (simple)
        self.create_input_section(main_frame)
        
        # Progress section
        self.create_progress_section(main_frame)
        
        # Console/Log section
        self.create_console_section(main_frame)
        
    def create_header(self, parent):
        """Create header with title and subtitle"""
        header_frame = ttk.Frame(parent, style="Dark.TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title with icon effect
        title_container = ttk.Frame(header_frame, style="Dark.TFrame")
        title_container.pack()
        
        # YouTube-style play button icon
        icon_canvas = tk.Canvas(title_container, width=50, height=50, 
                              bg="#1F2937", highlightthickness=0)
        icon_canvas.pack(side=tk.LEFT, padx=(0, 15))
        
        # Draw play button
        icon_canvas.create_oval(5, 5, 45, 45, fill="#FF0000", outline="")
        points = [20, 15, 20, 35, 35, 25]
        icon_canvas.create_polygon(points, fill="white", outline="")
        
        title_text_frame = ttk.Frame(title_container, style="Dark.TFrame")
        title_text_frame.pack(side=tk.LEFT)
        
        title_label = ttk.Label(title_text_frame, text="YouTube Playlist Downloader", 
                               style="Title.TLabel")
        title_label.pack(anchor=tk.W)
        
        subtitle_label = ttk.Label(title_text_frame, 
                                  text="Download entire playlists with embedded thumbnails",
                                  style="Subtitle.TLabel")
        subtitle_label.pack(anchor=tk.W)
        
    def create_input_section(self, parent):
        """Create simple URL input section with one Download button"""
        input_frame = ttk.Frame(parent, style="Dark.TFrame")
        input_frame.pack(fill=tk.X, pady=(0, 15))
        
        # URL Input
        url_label = ttk.Label(input_frame, text="Playlist URL:", style="Heading.TLabel")
        url_label.pack(anchor=tk.W, pady=(0, 5))
        
        url_container = ttk.Frame(input_frame, style="Dark.TFrame")
        url_container.pack(fill=tk.X)
        
        # Custom Entry with rounded corners effect
        self.url_entry = tk.Entry(url_container, textvariable=self.playlist_url,
                                 font=("Segoe UI", 11), bg="#374151", fg="white",
                                 insertbackground="white", relief=tk.FLAT, bd=10)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        
        # Download button (fetch + download)
        self.fetch_btn = ModernButton(url_container, text="Download", 
                                     command=self.download_playlist,
                                     bg="#10B981", width=120, height=40)
        self.fetch_btn.pack(side=tk.LEFT, padx=(10, 0))

    def download_playlist(self):
        """Fetch playlist info and immediately start downloading"""
        url = self.playlist_url.get().strip()
        if not url:
            messagebox.showwarning("Warning", "Please enter a playlist URL")
            return
        self.fetch_btn.set_state('disabled')
        self.log_message("Fetching playlist information...", "info")
        thread = threading.Thread(target=self._fetch_playlist_worker, args=(url, True))
        thread.daemon = True
        thread.start()
        
    def create_instructions_section(self, parent):
        """No-op: simple UI - instructions removed"""
        return
        
    def create_settings_section(self, parent):
        """No-op: simple UI - fixed downloads folder and quality"""
        return
        
    def create_progress_section(self, parent):
        """Create progress section"""
        progress_frame = ttk.Frame(parent, style="Dark.TFrame")
        progress_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Video list info
        self.video_info_label = ttk.Label(progress_frame, 
                                         text="No playlist loaded",
                                         style="Heading.TLabel")
        self.video_info_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Current video info
        self.current_video_label = ttk.Label(progress_frame,
                                            text="",
                                            style="Subtitle.TLabel")
        self.current_video_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Progress bar
        self.progress_bar = AnimatedProgressBar(progress_frame, width=860, height=8)
        self.progress_bar.pack(pady=(5, 10))
        
        # Control buttons (only Stop)
        button_frame = ttk.Frame(progress_frame, style="Dark.TFrame")
        button_frame.pack()
        
        self.stop_btn = ModernButton(button_frame, text="Stop",
                                    command=self.stop_download,
                                    bg="#EF4444", width=150, height=40)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        self.stop_btn.set_state('disabled')
        
    def create_console_section(self, parent):
        """Create console/log section"""
        console_frame = ttk.Frame(parent, style="Dark.TFrame")
        console_frame.pack(fill=tk.BOTH, expand=True)
        
        console_label = ttk.Label(console_frame, text="Download Log", style="Heading.TLabel")
        console_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Console with scrollbar
        console_container = ttk.Frame(console_frame, style="Dark.TFrame")
        console_container.pack(fill=tk.BOTH, expand=True)
        
        # Text widget for console
        self.console = tk.Text(console_container, height=10, bg="#111827", fg="#10B981",
                              font=("Consolas", 9), relief=tk.FLAT, wrap=tk.WORD,
                              insertbackground="#10B981")
        self.console.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(console_container, orient=tk.VERTICAL,
                                 command=self.console.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.console.config(yscrollcommand=scrollbar.set)
        
        # Configure tags for colored output
        self.console.tag_configure("info", foreground="#60A5FA")
        self.console.tag_configure("success", foreground="#10B981")
        self.console.tag_configure("error", foreground="#EF4444")
        self.console.tag_configure("warning", foreground="#F59E0B")
        
    def toggle_instructions(self):
        """Toggle instructions visibility with animation"""
        if self.instructions_visible.get():
            self.instructions_content.pack_forget()
            self.toggle_btn.config(text="▶ How to Get Playlist URL")
            self.instructions_visible.set(False)
        else:
            self.instructions_content.pack(fill=tk.X, pady=(5, 0))
            self.toggle_btn.config(text="▼ How to Get Playlist URL")
            self.instructions_visible.set(True)
            
    def browse_directory(self):
        """No-op: fixed downloads folder"""
        return
            
    def center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f"900x700+{x}+{y}")
        
    def log_message(self, message, tag="info"):
        """Add message to console"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.console.insert(tk.END, f"[{timestamp}] {message}\n", tag)
        self.console.see(tk.END)
        self.root.update_idletasks()
        
    def fetch_playlist_info(self):
        """Fetch playlist information"""
        url = self.playlist_url.get().strip()
        if not url:
            messagebox.showwarning("Warning", "Please enter a playlist URL")
            return
            
        self.fetch_btn.set_state('disabled')
        self.log_message("Fetching playlist information...", "info")
        
        # Run in thread to prevent GUI freezing
        thread = threading.Thread(target=self._fetch_playlist_worker, args=(url, False))
        thread.daemon = True
        thread.start()
        
    def _fetch_playlist_worker(self, url, auto_start=False):
        """Worker thread for fetching playlist"""
        try:
            yt = self.yt_dlp_path or "yt-dlp"
            cmd = [yt, "--flat-playlist", "--dump-json", url]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            videos = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    try:
                        video_data = json.loads(line)
                        videos.append({
                            'id': video_data.get('id'),
                            'url': f"https://www.youtube.com/watch?v={video_data['id']}",
                            'title': video_data.get('title', 'Unknown'),
                            'duration': video_data.get('duration', 0)
                        })
                    except json.JSONDecodeError:
                        continue
                        
            # Update info and optionally start download in sequence to avoid race
            self.root.after(0, self._update_playlist_info_and_maybe_start, videos, auto_start)
            
        except subprocess.CalledProcessError as e:
            self.root.after(0, lambda: self.log_message(f"Error: {e}", "error"))
            self.root.after(0, lambda: self.fetch_btn.set_state('normal'))
        except FileNotFoundError:
            self.root.after(0, lambda: self.log_message("Error: yt-dlp not found. Please install yt-dlp first.", "error"))
            self.root.after(0, lambda: messagebox.showerror("Error", "yt-dlp is not installed.\nPlease install it using: pip install yt-dlp"))
            self.root.after(0, lambda: self.fetch_btn.set_state('normal'))
            
    def _update_playlist_info(self, videos):
        """Update GUI with playlist information"""
        self.videos_info = videos
        self.total_videos = len(videos)
        
        if self.total_videos > 0:
            self.video_info_label.config(text=f"Found {self.total_videos} videos in playlist")
            self.log_message(f"Successfully fetched {self.total_videos} videos", "success")
        else:
            self.video_info_label.config(text="No videos found in playlist")
            self.log_message("No videos found in playlist", "warning")
            
        self.fetch_btn.set_state('normal')

    def _update_playlist_info_and_maybe_start(self, videos, auto_start):
        """Update playlist info and optionally kick off download immediately."""
        self._update_playlist_info(videos)
        if auto_start and self.total_videos > 0:
            self.start_download()
        
    def start_download(self):
        """Start downloading videos"""
        if not self.videos_info:
            messagebox.showwarning("Warning", "Please fetch playlist information first")
            return
            
        # Create output directory (constant)
        output_dir = DOWNLOADS_DIR
        os.makedirs(output_dir, exist_ok=True)
        
        self.is_downloading = True
        self.current_video = 0
        # No separate start button in simple UI
        self.stop_btn.set_state('normal')
        self.fetch_btn.set_state('disabled')
        
        # Fixed quality
        quality = "320k"
        
        # Start download thread
        thread = threading.Thread(target=self._download_worker, args=(output_dir, quality))
        thread.daemon = True
        thread.start()
        
    def _download_worker(self, output_dir, quality):
        """Worker thread for downloading videos"""
        # Continuity: collect already-downloaded video IDs and titles from filenames
        downloaded_ids = set()
        downloaded_titles = set()
        try:
            for path in glob.glob(os.path.join(output_dir, "*.mp3")):
                fname = os.path.basename(path)
                # Extract ID if present in suffix [VIDEOID]
                m_id = re.search(r"\[([A-Za-z0-9_-]{11})\]\.mp3$", fname)
                if m_id:
                    downloaded_ids.add(m_id.group(1))
                # Extract cleaned title regardless of ID presence
                m_title = re.match(r"^\d{3} - (.+?)(?: \[[A-Za-z0-9_-]{11}\])?\.mp3$", fname)
                if m_title:
                    downloaded_titles.add(m_title.group(1))
        except Exception:
            pass

        for i, video_info in enumerate(self.videos_info, start=1):
            if not self.is_downloading:
                break
            
            video_id = video_info.get('id')
            # Build sanitized title like our output format uses
            sanitized_title = re.sub(r'[<>:"/\\|?*]', '', video_info.get('title', ''))[:100]

            if (video_id and video_id in downloaded_ids) or (sanitized_title and sanitized_title in downloaded_titles):
                self.root.after(0, lambda vid=video_info['title']: self.log_message(f"✓ Skipping (already downloaded): {vid[:60]}", "success"))
                progress = (i / self.total_videos) * 100
                self.root.after(0, lambda p=progress: self.progress_bar.set_value(p))
                continue

            self.current_video = i
            self.root.after(0, lambda i=i, title=video_info['title']: 
                          self.current_video_label.config(text=f"Downloading {i}/{self.total_videos}: {title[:60]}..."))
            
            success = self._download_single_video(video_info, i, output_dir, quality)
            
            if success:
                self.root.after(0, lambda: self.log_message(f"✓ Downloaded: {video_info['title'][:60]}", "success"))
            else:
                self.root.after(0, lambda: self.log_message(f"✗ Failed: {video_info['title'][:60]}", "error"))
                
            # Update progress
            progress = (i / self.total_videos) * 100
            self.root.after(0, lambda p=progress: self.progress_bar.set_value(p))
            
            # Small delay between downloads
            if i < len(self.videos_info):
                time.sleep(2)
                
        self.root.after(0, self._download_complete)
        
    def _download_single_video(self, video_info, index, output_dir, quality):
        """Download a single video with thumbnail"""
        try:
            video_url = video_info['url']
            title = re.sub(r'[<>:"/\\|?*]', '', video_info['title'])[:100]
            video_id = video_info.get('id', '')
            
            tag = f" [{video_id}]" if video_id else ""
            base_filename = f"{index:03d} - {title}{tag}"
            mp3_file = os.path.join(output_dir, f"{base_filename}.mp3")
            thumbnail_file = os.path.join(output_dir, f"{base_filename}.jpg")
            
            # Download thumbnail
            self.root.after(0, lambda: self.log_message(f"  Downloading thumbnail...", "info"))
            if self._download_thumbnail(video_url, output_dir, base_filename):
                # Download audio
                self.root.after(0, lambda: self.log_message(f"  Downloading audio ({quality})...", "info"))
                if self._download_audio(video_url, mp3_file, quality):
                    # Embed thumbnail
                    if os.path.exists(thumbnail_file):
                        self.root.after(0, lambda: self.log_message(f"  Embedding thumbnail...", "info"))
                        self._embed_thumbnail_in_mp3(mp3_file, thumbnail_file)
                        os.remove(thumbnail_file)
                    return True
            return False
            
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"  Error: {str(e)}", "error"))
            return False
            
    def _download_thumbnail(self, video_url, output_dir, base_filename):
        """Download thumbnail for a video"""
        try:
            yt = self.yt_dlp_path or "yt-dlp"
            cmd = [yt, "--get-thumbnail", video_url]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            thumbnail_url = result.stdout.strip()
            
            if thumbnail_url:
                response = requests.get(thumbnail_url, timeout=30)
                response.raise_for_status()
                
                thumbnail_file = os.path.join(output_dir, f"{base_filename}.jpg")
                with open(thumbnail_file, 'wb') as f:
                    f.write(response.content)
                return True
        except:
            return False
            
    def _download_audio(self, video_url, output_path, quality):
        """Download audio for a video"""
        try:
            yt = self.yt_dlp_path or "yt-dlp"
            cmd = [
                yt, "-f", "bestaudio", "--extract-audio",
                "--audio-format", "mp3", "--audio-quality", quality,
                "--no-write-thumbnail", "-o", output_path, video_url
            ]
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            return True
        except:
            return False
            
    def _embed_thumbnail_in_mp3(self, mp3_file, thumbnail_file):
        """Embed thumbnail into MP3 file"""
        if MUTAGEN_AVAILABLE:
            try:
                audio = MP3(mp3_file)
                with open(thumbnail_file, 'rb') as f:
                    image_data = f.read()
                    
                apic = APIC(encoding=3, mime='image/jpeg', type=3,
                          desc='Cover', data=image_data)
                
                if not audio.tags:
                    audio.add_tags()
                audio.tags.add(apic)
                audio.save()
                return True
            except:
                pass
                
        # Fallback to ffmpeg
        try:
            temp_file = mp3_file + ".temp"
            ff = self.ffmpeg_path or "ffmpeg"
            cmd = [
                ff, "-i", mp3_file, "-i", thumbnail_file,
                "-map", "0:0", "-map", "1:0", "-c", "copy",
                "-id3v2_version", "3", temp_file, "-y"
            ]
            result = subprocess.run(cmd, capture_output=True)
            if result.returncode == 0:
                shutil.move(temp_file, mp3_file)
                return True
        except:
            pass
        return False
        
    def stop_download(self):
        """Stop downloading"""
        self.is_downloading = False
        self.log_message("Download stopped by user", "warning")
        # No separate start button in simple UI
        self.stop_btn.set_state('disabled')
        self.fetch_btn.set_state('normal')
        
    def _download_complete(self):
        """Called when download is complete"""
        self.current_video_label.config(text="Download complete!")
        self.log_message("All downloads completed!", "success")
        # No separate start button in simple UI
        self.stop_btn.set_state('disabled')
        self.fetch_btn.set_state('normal')
        self.progress_bar.set_value(100)
        
        messagebox.showinfo("Complete", f"Successfully downloaded {self.current_video} videos!")

def main():
    """Main function"""
    # No global dependency checks. We resolve local/bundled tools inside the GUI.

    os.makedirs(DOWNLOADS_DIR, exist_ok=True)

    root = tk.Tk()
    app = YouTubeDownloaderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
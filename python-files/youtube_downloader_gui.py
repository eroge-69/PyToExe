import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import yt_dlp
import os
import threading
import webbrowser

class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube MP3 Downloader")
        self.root.geometry("600x450")
        self.root.resizable(False, False)

        # Style configuration
        self.style = ttk.Style(self.root)
        self.style.theme_use('clam')

        # --- Variables ---
        self.url_var = tk.StringVar()
        self.save_path_var = tk.StringVar(value=os.path.join(os.getcwd(), "downloads"))
        self.video_info = {}

        # --- Main Frame ---
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- UI Widgets ---
        self._create_widgets(main_frame)

    # --- START OF NEW/MODIFIED SECTION ---

    def show_context_menu(self, event):
        """Create and display the context menu."""
        # Check if there is any selected text to decide if "Cut" and "Copy" should be active
        try:
            # selection_get() will raise an error if nothing is selected
            self.url_entry.selection_get()
            self.context_menu.entryconfig("Cut", state="normal")
            self.context_menu.entryconfig("Copy", state="normal")
        except tk.TclError:
            # Nothing is selected, disable "Cut" and "Copy"
            self.context_menu.entryconfig("Cut", state="disabled")
            self.context_menu.entryconfig("Copy", state="disabled")

        # Check if there is text on the clipboard to decide if "Paste" should be active
        try:
            self.root.clipboard_get()
            self.context_menu.entryconfig("Paste", state="normal")
        except tk.TclError:
            # Clipboard is empty or doesn't contain text, disable "Paste"
            self.context_menu.entryconfig("Paste", state="disabled")

        self.context_menu.tk_popup(event.x_root, event.y_root)

    def custom_cut(self):
        """Custom cut function."""
        self.custom_copy() # First, copy the selected text
        self.url_entry.delete(tk.SEL_FIRST, tk.SEL_LAST) # Then, delete it

    def custom_copy(self):
        """Custom copy function."""
        try:
            selected_text = self.url_entry.selection_get()
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
        except tk.TclError:
            pass # Do nothing if no text is selected

    def custom_paste(self):
        """Custom paste function that directly inserts clipboard content."""
        try:
            # Get text from the clipboard
            clipboard_text = self.root.clipboard_get()
            # Insert it at the cursor's position
            self.url_entry.insert(tk.INSERT, clipboard_text)
        except tk.TclError:
            # This error occurs if the clipboard is empty or contains non-text data
            print("Clipboard is empty or does not contain text.")
            pass

    # --- END OF NEW/MODIFIED SECTION ---

    def _create_widgets(self, parent):
        # URL Entry
        ttk.Label(parent, text="YouTube Video URL:").grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.url_entry = ttk.Entry(parent, textvariable=self.url_var, width=60)
        self.url_entry.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        # --- MODIFIED: Context Menu Setup ---
        # Create the context menu and link it to our custom functions
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Cut", command=self.custom_cut)
        self.context_menu.add_command(label="Copy", command=self.custom_copy)
        self.context_menu.add_command(label="Paste", command=self.custom_paste)

        # Bind the right-click event to show our menu
        self.url_entry.bind("<Button-3>", self.show_context_menu)
        # --- END OF MODIFICATION ---

        # Get Info Button
        self.info_button = ttk.Button(parent, text="Get Video Info", command=self.fetch_video_info)
        self.info_button.grid(row=1, column=2, padx=(10, 0), pady=(0, 10))

        # Preview Frame
        preview_frame = ttk.LabelFrame(parent, text="Video Preview", padding="10")
        preview_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(0, 20))

        self.preview_label = ttk.Label(preview_frame, text="Enter a URL and click 'Get Video Info' to see details.", wraplength=500)
        self.preview_label.pack(pady=5)

        self.view_on_yt_link = ttk.Label(preview_frame, text="", foreground="blue", cursor="hand2")
        self.view_on_yt_link.pack(pady=5)
        self.view_on_yt_link.bind("<Button-1>", lambda e: self.open_video_in_browser())

        # Save Path Selection
        ttk.Label(parent, text="Save to Folder:").grid(row=3, column=0, sticky="w", pady=(0, 5))
        self.path_entry = ttk.Entry(parent, textvariable=self.save_path_var, state="readonly", width=60)
        self.path_entry.grid(row=4, column=0, columnspan=2, sticky="ew")

        self.browse_button = ttk.Button(parent, text="Browse...", command=self.browse_directory)
        self.browse_button.grid(row=4, column=2, padx=(10, 0))

        # Download Button
        self.download_button = ttk.Button(parent, text="Download MP3", command=self.start_download, state="disabled")
        self.download_button.grid(row=5, column=0, columnspan=3, pady=20, ipady=5)

        # Status Bar
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=6, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        status_frame.columnconfigure(0, weight=1)

        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.grid(row=0, column=0, sticky="w")

        self.progress_bar = ttk.Progressbar(status_frame, orient="horizontal", mode="determinate")
        self.progress_bar.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)


    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.save_path_var.set(directory)

    def fetch_video_info(self):
        url = self.url_var.get()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL.")
            return
        self.status_label.config(text="Fetching video info...")
        self.info_button.config(state="disabled")
        self.download_button.config(state="disabled")
        self.progress_bar['value'] = 0
        threading.Thread(target=self._get_info_thread, args=(url,), daemon=True).start()

    def _get_info_thread(self, url):
        try:
            ydl_opts = {'noplaylist': True, 'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.video_info = ydl.extract_info(url, download=False)
            self.root.after(0, self.update_preview)
        except Exception as e:
            self.root.after(0, self.show_error, f"Could not fetch info: {e}")

    def update_preview(self):
        title = self.video_info.get('title', 'N/A')
        uploader = self.video_info.get('uploader', 'N/A')
        duration = self.video_info.get('duration_string', 'N/A')
        preview_text = f"Title: {title}\nUploader: {uploader}\nDuration: {duration}"
        self.preview_label.config(text=preview_text)
        self.view_on_yt_link.config(text="View on YouTube")
        self.status_label.config(text="Info loaded. Ready to download.")
        self.info_button.config(state="normal")
        self.download_button.config(state="normal")

    def open_video_in_browser(self):
        if self.video_info and 'webpage_url' in self.video_info:
            webbrowser.open_new(self.video_info['webpage_url'])

    def start_download(self):
        self.download_button.config(state="disabled")
        self.info_button.config(state="disabled")
        self.progress_bar['value'] = 0
        self.status_label.config(text="Starting download...")
        threading.Thread(target=self._download_thread, daemon=True).start()

    def _download_thread(self):
        video_url = self.url_var.get()
        output_path = self.save_path_var.get()
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
            'noplaylist': True,
            'progress_hooks': [self.progress_hook],
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
        except Exception as e:
            self.root.after(0, self.show_error, f"An error occurred: {e}")

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            if total_bytes:
                downloaded_bytes = d.get('downloaded_bytes')
                percentage = (downloaded_bytes / total_bytes) * 100
                self.root.after(0, self.update_progress, percentage, "Downloading...")
        elif d['status'] == 'finished':
            self.root.after(0, self.update_progress, 100, "Download complete. Converting to MP3...")
            self.root.after(1500, self.download_complete)

    def update_progress(self, value, text):
        self.progress_bar['value'] = value
        self.status_label.config(text=text)

    def download_complete(self):
        self.status_label.config(text="MP3 saved successfully!")
        messagebox.showinfo("Success", f"Download complete!\nFile saved in: {self.save_path_var.get()}")
        self.progress_bar['value'] = 0
        self.download_button.config(state="normal")
        self.info_button.config(state="normal")

    def show_error(self, message):
        self.status_label.config(text="Error occurred.")
        messagebox.showerror("Error", message)
        self.info_button.config(state="normal")
        if self.video_info:
            self.download_button.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()
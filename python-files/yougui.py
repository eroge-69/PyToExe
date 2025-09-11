import customtkinter
import yt_dlp
import threading
import queue
import os

# Set the appearance mode and default color theme for the GUI
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # --- CONFIGURE THE MAIN WINDOW ---
        self.title("Zenith YouTube Downloader")
        self.geometry("720x480")
        self.grid_columnconfigure(0, weight=1)

        # Queue for thread-safe communication between download thread and GUI
        self.download_queue = queue.Queue()
        self.after(100, self.process_queue) # Start checking the queue

        # --- CREATE WIDGETS ---
        self.title_label = customtkinter.CTkLabel(self, text="Zenith Downloader", font=customtkinter.CTkFont(size=30, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.url_frame = customtkinter.CTkFrame(self)
        self.url_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.url_frame.grid_columnconfigure(0, weight=1)
        
        self.url_entry = customtkinter.CTkEntry(self.url_frame, placeholder_text="Paste your YouTube video or short URL here...", height=40)
        self.url_entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.download_button = customtkinter.CTkButton(self, text="Download Video", command=self.start_download_thread, height=40, font=customtkinter.CTkFont(size=16, weight="bold"))
        self.download_button.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.status_label = customtkinter.CTkLabel(self, text="", font=customtkinter.CTkFont(size=14))
        self.status_label.grid(row=3, column=0, padx=20, pady=10)

        self.progress_bar = customtkinter.CTkProgressBar(self, mode='determinate')
        self.progress_bar.set(0)
        self.progress_bar.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

    def start_download_thread(self):
        """Disables the button and starts the download in a new thread."""
        url = self.url_entry.get().strip()
        if not url:
            self.status_label.configure(text="Please enter a URL first!", text_color="orange")
            return

        # Disable button and reset UI elements for a new download
        self.download_button.configure(state="disabled", text="Processing...")
        self.progress_bar.set(0)
        self.status_label.configure(text="")

        # The download runs in a separate thread to not freeze the app
        thread = threading.Thread(target=self.download_youtube_video_with_my_code, args=(url, self.download_queue))
        thread.start()

    def download_youtube_video_with_my_code(self, url, q):
        """
        This is YOUR download logic, adapted to run in the background thread.
        It takes the queue as an argument to report progress back to the GUI.
        """
        def hook(d):
            """
            This is YOUR hook function. Instead of printing, it puts the
            status dictionary into the queue for the GUI to process.
            """
            q.put(d)

        # --- THIS IS YOUR EXACT ydl_opts DICTIONARY ---
        ydl_opts = {
            'format': 'best[ext=mp4][vcodec^=avc1][acodec^=mp4a]/best',
            'merge_output_format': 'mp4',
            'outtmpl': '%(title)s.%(ext)s',
            'noplaylist': True,
            'progress_hooks': [hook], # The hook is now GUI-aware
        }

        try:
            # --- THIS IS YOUR EXACT DOWNLOAD EXECUTION CODE ---
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                q.put({'status': 'pre-processing'})
                ydl.download([url])
        except Exception as e:
            # If an error happens, put it in the queue for the GUI to display
            q.put({'status': 'error', 'error': str(e)})

    def process_queue(self):
        """
        Checks the queue for messages from the download thread and updates the GUI.
        This runs every 100ms in the main GUI thread.
        """
        try:
            message = self.download_queue.get_nowait()
            
            if message['status'] == 'pre-processing':
                self.download_button.configure(text="Downloading...")

            elif message['status'] == 'downloading':
                # Extract percentage and format it for the progress bar
                percent_str = message.get('_percent_str', '0%').strip().replace('%', '')
                try:
                    percent = float(percent_str) / 100
                    self.progress_bar.set(percent)
                    
                    # Update status label with live data
                    speed = message.get('_speed_str', 'N/A')
                    eta = message.get('_eta_str', 'N/A')
                    self.status_label.configure(text=f"{percent:.0%}  |  Speed: {speed}  |  ETA: {eta}")
                except (ValueError, TypeError):
                    pass # Ignore if percentage is not a valid number for a moment

            elif message['status'] == 'finished':
                self.progress_bar.set(1)
                filename = os.path.basename(message.get('filename', 'video.mp4'))
                self.status_label.configure(text=f"✅ Download complete! Saved as: {filename}", text_color="lightgreen")
                self.download_button.configure(state="normal", text="Download Another Video")

            elif message['status'] == 'error':
                error_msg = message.get('error', 'An unknown error occurred.')
                self.status_label.configure(text=f"❌ Error: {error_msg}", text_color="#FF5555") # A soft red color
                self.download_button.configure(state="normal", text="Download Video")
                self.progress_bar.set(0)

        except queue.Empty:
            pass # No new message in the queue
        finally:
            # Schedule this function to run again after 100ms
            self.after(100, self.process_queue)

if __name__ == "__main__":
    app = App()
    app.mainloop()


import os
import random
import subprocess
import platform
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from PIL import Image, ImageTk
import threading


class VideoSelectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Video Selector")
        self.root.geometry("800x600")
        self.root.configure(bg="#2c3e50")
        self.root.minsize(700, 500)

        # Video extensions
        self.video_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm', '.m4v']

        # Style configuration
        self.setup_styles()

        # Create UI
        self.create_widgets()

        # Load videos
        self.video_files = []
        self.load_videos()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Configure styles
        self.style.configure('Title.TLabel',
                             background='#2c3e50',
                             foreground='#ecf0f1',
                             font=('Arial', 18, 'bold'))

        self.style.configure('Subtitle.TLabel',
                             background='#2c3e50',
                             foreground='#bdc3c7',
                             font=('Arial', 12))

        self.style.configure('Action.TButton',
                             font=('Arial', 12, 'bold'),
                             padding=10,
                             background='#3498db',
                             foreground='white')

        self.style.map('Action.TButton',
                       background=[('active', '#2980b9')])

        self.style.configure('Listbox.TFrame',
                             background='#34495e')

        self.style.configure('Status.TLabel',
                             background='#2c3e50',
                             foreground='#ecf0f1',
                             font=('Arial', 10))

    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)

        # Title
        title_label = ttk.Label(main_frame, text="🎬 Random Video Selector", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # Directory info
        self.dir_label = ttk.Label(main_frame, text=f"📁 Directory: {os.getcwd()}", style='Subtitle.TLabel')
        self.dir_label.grid(row=1, column=0, columnspan=2, pady=(0, 20), sticky=tk.W)

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(0, 20))

        # Random button
        self.random_btn = ttk.Button(button_frame, text="🎲 Random Video",
                                     command=self.choose_random_video, style='Action.TButton')
        self.random_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Refresh button
        self.refresh_btn = ttk.Button(button_frame, text="🔄 Refresh List",
                                      command=self.load_videos, style='Action.TButton')
        self.refresh_btn.pack(side=tk.LEFT)

        # Listbox frame
        list_frame = ttk.Frame(main_frame, style='Listbox.TFrame', padding="10")
        list_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # List label
        ttk.Label(list_frame, text="Available Videos:",
                  background='#34495e', foreground='#ecf0f1').pack(anchor=tk.W)

        # Listbox with scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        self.video_listbox = tk.Listbox(list_container, bg='#2c3e50', fg='#ecf0f1',
                                        selectbackground='#3498db', font=('Arial', 11),
                                        relief=tk.FLAT, highlightthickness=0)

        scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.video_listbox.yview)
        self.video_listbox.configure(yscrollcommand=scrollbar.set)

        self.video_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind double-click to play video
        self.video_listbox.bind('<Double-Button-1>', self.play_selected_video)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, style='Status.TLabel')
        status_bar.grid(row=4, column=0, columnspan=2, pady=(10, 0), sticky=tk.W)

        # Selected video info
        self.selected_var = tk.StringVar()
        self.selected_var.set("No video selected")
        selected_label = ttk.Label(main_frame, textvariable=self.selected_var, style='Status.TLabel')
        selected_label.grid(row=5, column=0, columnspan=2, pady=(5, 0), sticky=tk.W)

    def load_videos(self):
        """Load video files from current directory"""
        self.status_var.set("Loading videos...")
        self.root.update()

        try:
            self.video_files = []
            all_files = os.listdir(os.getcwd())

            for f in all_files:
                if os.path.isfile(f) and any(f.lower().endswith(ext) for ext in self.video_extensions):
                    self.video_files.append(f)

            # Update listbox
            self.video_listbox.delete(0, tk.END)
            for video in sorted(self.video_files):
                self.video_listbox.insert(tk.END, video)

            self.status_var.set(f"Found {len(self.video_files)} video files")
            self.selected_var.set("No video selected")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load videos: {str(e)}")
            self.status_var.set("Error loading videos")

    def choose_random_video(self):
        """Choose a random video and ask if user wants to play it"""
        if not self.video_files:
            messagebox.showinfo("No Videos", "No video files found in the current directory!")
            return

        # Choose random video
        chosen_video = random.choice(self.video_files)
        chosen_path = os.path.join(os.getcwd(), chosen_video)

        # Update selected video display
        self.selected_var.set(f"Selected: {chosen_video}")

        # Ask user if they want to play it
        response = messagebox.askyesno(
            "Random Video Selected",
            f"🎲 Selected: {chosen_video}\n\nDo you want to play this video?",
            icon='question'
        )

        if response:
            self.play_video(chosen_path)
        else:
            self.status_var.set("Video not played - select another one")

    def play_selected_video(self, event=None):
        """Play the video selected in the listbox"""
        selection = self.video_listbox.curselection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a video from the list first!")
            return

        selected_video = self.video_listbox.get(selection[0])
        video_path = os.path.join(os.getcwd(), selected_video)
        self.play_video(video_path)

    def play_video(self, video_path):
        """Play the video using the default system player"""
        self.status_var.set(f"Playing: {os.path.basename(video_path)}")

        # Play video in a separate thread to avoid freezing the GUI
        def play_thread():
            try:
                if platform.system() == 'Darwin':  # macOS
                    subprocess.call(('open', video_path))
                elif platform.system() == 'Windows':  # Windows
                    os.startfile(video_path)
                else:  # Linux variants
                    subprocess.call(('xdg-open', video_path))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "Playback Error",
                    f"Could not play video: {str(e)}"
                ))
                self.root.after(0, lambda: self.status_var.set("Playback failed"))

        threading.Thread(target=play_thread, daemon=True).start()


def main():
    root = tk.Tk()
    app = VideoSelectorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
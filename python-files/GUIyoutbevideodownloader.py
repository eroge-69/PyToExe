import tkinter as tk
from tkinter import ttk, messagebox
from yt_dlp import YoutubeDL
import os
import tkinter.font as tkfont

class YouTubeDownloader(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Anant's YouTube Downloader")
        self.geometry("720x500")
        self.theme = "dark"
        self.configure(bg="black")
        self.resizable(False, False)

        try:
            self.bg_image = tk.PhotoImage(file="Background .png")
        except Exception as e:
            messagebox.showerror("Image Load Error", f"Could not load background image.\n{e}")
            self.bg_image = None

        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        if self.bg_image:
            self.bg = self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")

        self.ui_frame = tk.Frame(self.canvas, bg="black")
        self.canvas_frame = self.canvas.create_window(0, 0, window=self.ui_frame, anchor="nw")

        self.create_widgets()

        self.canvas.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        if self.bg_image:
            self.canvas.coords(self.bg, 0, 0)
            self.canvas.itemconfig(self.bg, image=self.bg_image)
        self.canvas.itemconfig(self.canvas_frame, width=event.width, height=event.height)
        self.fade_gradient(event.width, event.height)

    def fade_gradient(self, width, height):
        try:
            self.canvas.delete("fade")
        except:
            pass
        for i in range(100):
            r = 0
            g = 0
            b = int(255 * i / 100)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.canvas.create_rectangle(0, height - 100 + i, width, height - 100 + i + 1, fill=color, outline="", tags="fade")

    def toggle_theme(self):
        if self.theme == "dark":
            self.theme = "light"
            bg = "#f0f0f0"
            fg = "#000000"
            entry_bg = "white"
            self.switch_canvas.itemconfig(self.switch_thumb, fill="white")
            self.switch_canvas.coords(self.switch_thumb, 42, 2, 58, 18)
        else:
            self.theme = "dark"
            bg = "black"
            fg = "white"
            entry_bg = "#222"
            self.switch_canvas.itemconfig(self.switch_thumb, fill="black")
            self.switch_canvas.coords(self.switch_thumb, 2, 2, 18, 18)

        self.configure(bg=bg)
        self.canvas.configure(bg=bg)
        self.ui_frame.configure(bg=bg)

        for widget in self.ui_frame.winfo_children():
            if isinstance(widget, (tk.Label, tk.Button, tk.Radiobutton, tk.Frame)):
                try:
                    widget.configure(bg=bg, fg=fg)
                except:
                    pass
            if isinstance(widget, tk.Entry):
                widget.configure(bg=entry_bg, fg=fg, insertbackground=fg)

    def create_widgets(self):
        header_frame = tk.Frame(self.ui_frame, bg="black")
        header_frame.pack(pady=10)

        try:
            self.logo = tk.PhotoImage(file="Infinity TechXcell Logo.png").subsample(12, 12)
            tk.Label(header_frame, image=self.logo, bg="black").pack(side="left", padx=10)
        except:
            self.logo = None

        self.draw_colored_heading(header_frame)

        switch_frame = tk.Frame(self.ui_frame, bg="black")
        switch_frame.pack(pady=5)
        tk.Label(switch_frame, text="Dark", fg="white", bg="black").pack(side="left")

        self.switch_canvas = tk.Canvas(switch_frame, width=60, height=22, bg="gray", highlightthickness=0)
        self.switch_canvas.pack(side="left", padx=5)
        self.switch_canvas.create_rectangle(0, 0, 60, 22, fill="gray", outline="", width=0, tags="track")
        self.switch_thumb = self.switch_canvas.create_oval(2, 2, 18, 18, fill="black", outline="black")
        self.switch_canvas.bind("<Button-1>", lambda e: self.toggle_theme())

        tk.Label(switch_frame, text="Light", fg="white", bg="black").pack(side="left")

        tk.Label(self.ui_frame, text="Paste YouTube Link:", fg="white", bg="black", font=("Arial", 14)).pack(pady=10)
        self.url_var = tk.StringVar()
        self.url_entry = tk.Entry(self.ui_frame, textvariable=self.url_var, width=60, font=("Arial", 12),
                                  bg="#222", fg="white", insertbackground="white")
        self.url_entry.pack(pady=5)

        tk.Button(self.ui_frame, text="Fetch Formats", command=self.fetch_formats,
                  bg="blue", fg="white", font=("Arial", 12)).pack(pady=10)

        self.format_var = tk.StringVar(value="video")
        format_frame = tk.Frame(self.ui_frame, bg="black")
        format_frame.pack()
        tk.Radiobutton(format_frame, text="Video", variable=self.format_var, value="video",
                       bg="black", fg="white", selectcolor="black", command=self.update_quality_menu).pack(side="left", padx=10)
        tk.Radiobutton(format_frame, text="Audio (MP3)", variable=self.format_var, value="audio",
                       bg="black", fg="white", selectcolor="black", command=self.update_quality_menu).pack(side="left", padx=10)

        self.quality_var = tk.StringVar()
        self.quality_menu = ttk.Combobox(self.ui_frame, textvariable=self.quality_var, state="readonly", width=30)
        self.quality_menu.pack(pady=10)

        tk.Button(self.ui_frame, text="Download", command=self.download_video, bg="purple", fg="white",
                  font=("Arial", 12)).pack(pady=10)

        self.progress = ttk.Progressbar(self.ui_frame, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=5)
        self.speed_label = tk.Label(self.ui_frame, text="Speed: 0 KB/s", fg="white", bg="black")
        self.speed_label.pack()

    def draw_colored_heading(self, parent):
        canvas = tk.Canvas(parent, width=600, height=60, bg="black", highlightthickness=0)
        canvas.pack(side="left", padx=10)

        available_fonts = tkfont.families()
        heading_font = ("Futura Md BT", 22, "bold") if "Futura Md BT" in available_fonts else ("Arial", 22, "bold")
        font_obj = tkfont.Font(family=heading_font[0], size=22, weight="bold")

        parts = [
            ("Anant's", "#00f0ff"),
            ("YouTube", "#ff0033"),
            ("Video", "#ffaa00"),
            ("Downloader", "#00ff99")
        ]

        x = 10
        for word, color in parts:
            canvas.create_text(x, 30, text=word + " ", fill=color, font=heading_font, anchor='w')
            x += font_obj.measure(word + " ")

    def fetch_formats(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Missing URL", "Please enter a valid YouTube URL.")
            return

        ydl_opts = {'quiet': True, 'skip_download': True}
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            formats = info.get("formats", [])
            self.audio_choices = {}
            self.video_choices = {}

            for f in formats:
                if f.get("vcodec") == "none":
                    label = f"{f.get('abr', 'Unknown')}kbps"
                    self.audio_choices[label] = f["format_id"]
                elif f.get("acodec") == "none":
                    height = f.get("height")
                    if height:
                        label = f"{height}p"
                        self.video_choices[label] = f["format_id"]

            self.update_quality_menu()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_quality_menu(self):
        if self.format_var.get() == "audio":
            self.quality_map = self.audio_choices
        else:
            self.quality_map = self.video_choices

        self.quality_menu['values'] = list(self.quality_map.keys())
        if self.quality_map:
            self.quality_var.set(list(self.quality_map.keys())[0])

    def download_video(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Enter a valid URL")
            return

        selected_quality = self.quality_var.get()
        output_template = os.path.join(os.getcwd(), "%(title)s.%(ext)s")

        if self.format_var.get() == "audio":
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_template,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'progress_hooks': [self.progress_hook],
            }
        else:
            fid = self.quality_map.get(selected_quality, "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4")
            ydl_opts = {
                'format': f"{fid}+bestaudio/best",
                'outtmpl': output_template,
                'merge_output_format': 'mp4',
                'progress_hooks': [self.progress_hook]
            }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            retry = messagebox.askyesno("Download Complete", "Download completed successfully!\n\nWould you like to download another video?")
            if retry:
                self.url_var.set("")
                self.quality_menu.set("")
                self.progress["value"] = 0
                self.speed_label.config(text="Speed: 0 KB/s")
                self.url_entry.focus_set()
            else:
                self.quit()
        except Exception as e:
            messagebox.showerror("Download Error", str(e))

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            downloaded = d.get("downloaded_bytes", 0)
            total = d.get("total_bytes", 1)
            speed = d.get("speed", 0)
            percent = int(downloaded * 100 / total)
            self.progress["value"] = percent
            self.speed_label.config(text=f"Speed: {round(speed / 1024, 2)} KB/s")
            self.update_idletasks()

if __name__ == "__main__":
    app = YouTubeDownloader()
    app.mainloop()

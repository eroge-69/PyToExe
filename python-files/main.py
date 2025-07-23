import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import random
from moviepy.editor import VideoFileClip, concatenate_videoclips, vfx
import threading

class YTPApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Spigottan YTP Generator")
        self.video_path = ""
        self.effects = {"Threshold": tk.BooleanVar(),
                        "Zoom": tk.BooleanVar(),
                        "Mosaic": tk.BooleanVar()}
        self.build_gui()

    def build_gui(self):
        frm = tk.Frame(self.root, padx=10, pady=10)
        frm.pack()

        tk.Label(frm, text="Video:").grid(row=0, column=0, sticky="e")
        self.path_entry = tk.Entry(frm, width=40)
        self.path_entry.grid(row=0, column=1)
        tk.Button(frm, text="Browse", command=self.browse_file).grid(row=0, column=2)

        tk.Label(frm, text="Effects:").grid(row=1, column=0, sticky="ne")
        eff_frame = tk.Frame(frm)
        eff_frame.grid(row=1, column=1, sticky="w")
        for i, (name, var) in enumerate(self.effects.items()):
            tk.Checkbutton(eff_frame, text=name, variable=var).grid(row=i, column=0, sticky="w")

        tk.Button(frm, text="Render", command=self.start_render).grid(row=2, column=1, pady=10)

    def browse_file(self):
        self.video_path = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4")])
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, self.video_path)

    def start_render(self):
        if not self.video_path:
            messagebox.showerror("Error", "No video selected.")
            return
        threading.Thread(target=self.render_video).start()

    def render_video(self):
        try:
            clip = VideoFileClip(self.video_path).subclip(0, 20)
            clips = []
            for _ in range(15):
                sub = clip.subclip(random.uniform(0, 15), random.uniform(15, 20))
                if self.effects["Zoom"].get():
                    sub = sub.fx(vfx.crop, x_center=sub.w//2, y_center=sub.h//2, width=sub.w//2, height=sub.h//2)
                    sub = sub.resize((clip.w, clip.h))
                if self.effects["Threshold"].get():
                    sub = sub.fx(vfx.lum_contrast, 0, 150, 255)
                if self.effects["Mosaic"].get():
                    sub = sub.resize(0.1).resize(10)
                clips.append(sub)
            final = concatenate_videoclips(clips)
            final.write_videofile("output/ytp_result.mp4", fps=24)
            messagebox.showinfo("Done", "Video saved as output/ytp_result.mp4")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = YTPApp(root)
    root.mainloop()

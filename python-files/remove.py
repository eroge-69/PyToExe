import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import cv2
import numpy as np
import os
import subprocess

class WatermarkRemoverGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Watermark Remover by Moh Sagor")
        self.root.geometry("900x650")

        self.video_path = ""
        self.frame = None
        self.tk_image = None
        self.canvas_image = None
        self.rect_start = None
        self.rect_end = None
        self.drawing = False
        self.display_size = (800, 450)

        # Top Controls
        control_frame = tk.Frame(root)
        control_frame.pack(pady=10)

        tk.Button(control_frame, text="Choose Video", command=self.choose_video).pack(side=tk.LEFT, padx=10)
        self.remove_btn = tk.Button(control_frame, text="Remove Watermark (AI)", command=self.remove_watermark, state='disabled')
        self.remove_btn.pack(side=tk.LEFT, padx=10)

        # Canvas
        self.canvas = tk.Canvas(root, cursor="cross", bg="gray", width=800, height=450)
        self.canvas.pack(pady=10)
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

        # Progress
        self.progress_label = tk.Label(root, text="", font=("Arial", 12))
        self.progress_label.pack()
        self.progress = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=700, mode='determinate')
        self.progress.pack(pady=5)

    def choose_video(self):
        path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv")])
        if not path:
            return

        self.video_path = path
        cap = cv2.VideoCapture(path)
        ret, frame = cap.read()
        cap.release()

        if not ret:
            messagebox.showerror("Error", "Failed to load video.")
            return

        self.frame = frame
        self.rect_start = self.rect_end = None
        self.remove_btn.config(state='disabled')
        self.display_frame()

    def display_frame(self):
        image = cv2.cvtColor(self.frame.copy(), cv2.COLOR_BGR2RGB)
        img = Image.fromarray(image)

        # Scale to fit max 800x450 while keeping aspect ratio
        original_w, original_h = img.size
        max_w, max_h = 800, 450
        ratio = min(max_w / original_w, max_h / original_h)
        new_w, new_h = int(original_w * ratio), int(original_h * ratio)
        self.display_size = (new_w, new_h)

        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(img)
        self.canvas.config(width=new_w, height=new_h)
        self.canvas.delete("all")
        self.canvas_image = self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

        if self.rect_start and self.rect_end:
            self.canvas.create_rectangle(*self.rect_start, *self.rect_end, outline="green", width=2)

    def on_mouse_down(self, event):
        self.rect_start = (event.x, event.y)
        self.drawing = True

    def on_mouse_drag(self, event):
        if not self.drawing:
            return
        self.rect_end = (event.x, event.y)
        self.display_frame()

    def on_mouse_up(self, event):
        self.drawing = False
        if self.rect_start and self.rect_end:
            self.remove_btn.config(state='normal')

    def remove_watermark(self):
        self.progress_label.config(text="Removing watermark...")
        self.progress["value"] = 0
        self.root.update_idletasks()

        cap = cv2.VideoCapture(self.video_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        output_no_audio = os.path.splitext(self.video_path)[0] + "_no_audio.mp4"
        out = cv2.VideoWriter(output_no_audio, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

        # Convert selection to actual video coordinates
        x1, y1 = self.rect_start
        x2, y2 = self.rect_end
        x1, x2 = sorted([x1, x2])
        y1, y2 = sorted([y1, y2])
        scale_x = width / self.display_size[0]
        scale_y = height / self.display_size[1]
        x1 = int(x1 * scale_x)
        x2 = int(x2 * scale_x)
        y1 = int(y1 * scale_y)
        y2 = int(y2 * scale_y)

        frame_no = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            mask = np.zeros(frame.shape[:2], dtype="uint8")
            mask[y1:y2, x1:x2] = 255
            result = cv2.inpaint(frame, mask, 3, cv2.INPAINT_TELEA)
            out.write(result)

            frame_no += 1
            percent = int((frame_no / total_frames) * 100)
            self.progress["value"] = percent
            self.progress_label.config(text=f"Processing... {percent}%")
            self.root.update_idletasks()

        cap.release()
        out.release()

        # Combine audio using FFmpeg
        final_output = self.combine_audio(output_no_audio, self.video_path)
        os.remove(output_no_audio)
        
        self.progress_label.config(text="✅ Done")
        messagebox.showinfo("Success", f"Watermark removed.\nSaved to:\n{final_output}")

    def combine_audio(self, video_path, original_path):
        final_output = os.path.splitext(video_path)[0] + "_moh_sagor.mp4"
        command = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", original_path,
            "-c", "copy",
            "-map", "0:v:0",
            "-map", "1:a:0",
            final_output
        ]
        try:
            subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            messagebox.showwarning("FFmpeg Error", f"Audio merging failed:\n{e}")
            return video_path
        return final_output

if __name__ == "__main__":
    root = tk.Tk()
    app = WatermarkRemoverGUI(root)
    root.mainloop()

